"""Local, read-only usage evidence. No SDK, model, or network connection is used.

collect() counts signals, not user tasks. A qualifying read, execution or tool call
has an event id; the same id can belong to both a skill and its parent plugin.
The result contains aggregates, never arguments, commands or transcript content.
"""
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import xml.etree.ElementTree as ET

NAME = re.compile(r"^[\w.-]+(?::[\w.-]+)*$")
MAX_LINE = 8 * 1024 * 1024


def _object(value):
    return value if isinstance(value, dict) else {}


def _parse(raw):
    try:
        return _object(json.loads(raw))
    except (ValueError, UnicodeError, RecursionError, TypeError):
        return {}


def _time(value):
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value / 1000 if value >= 10**11 else value
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                return dt.timestamp()
    except (ValueError, OverflowError, OSError):
        pass
    return None


class _Evidence:
    def __init__(self, start, end, excluded, known_paths):
        self.start, self.end = start.timestamp(), end.timestamp()
        self.tz, self.excluded = end.tzinfo, excluded
        self.paths = {}
        self.known_paths = known_paths
        self.tables = {t: defaultdict(dict) for t in ("skills", "plugins", "skill_paths")}
        self.observed = set()
        self.projected_sessions = set()
        self.earlier = False
        self.issues = defaultdict(int)
        self.sources = set()
        self.ambiguous_native = {}
        self.ambiguous_invocation = {}
        self.hints = defaultdict(dict)
        self.blind_spots = []

    def activity(self, session, ts):
        if not session or session in self.excluded or ts is None or ts > self.end:
            return False
        if ts < self.start:
            self.earlier = True
            return False
        self.observed.add(datetime.fromtimestamp(ts, self.tz).date().isoformat())
        return True

    def add(self, table, name, event, session, ts):
        if name and (table == "skill_paths" or NAME.fullmatch(name)):
            self.tables[table][name].setdefault(event, (session, ts))

    def _targets(self, name, path):
        if path:
            if path not in self.paths:
                try:
                    self.paths[path] = str(path.resolve())
                except (OSError, RuntimeError):
                    self.paths[path] = str(path)
            canonical = self.paths[path]
            yield "skill_paths", canonical
            if not name:
                name = self.known_paths.get(canonical)
        if name and NAME.fullmatch(name):
            yield "skills", name
            if ":" in name and not name.startswith("anthropic-skills:"):
                yield "plugins", name.split(":", 1)[0]

    def skill(self, name, event, session, ts, path=None):
        for table, key in self._targets(name, path):
            self.add(table, key, event, session, ts)

    def invocation(self, name, session, ts, path=None):
        # A typed selection or rendered skill body often accompanies its tool use.
        # Preserve at most one extra floor per session when no such event survived.
        for table, key in self._targets(name, path):
            row = self.hints[(table, key)]
            row[session] = max(ts, row.get(session, ts))

    def flush_invocations(self):
        for (table, name), hints in self.hints.items():
            events = self.tables[table][name]
            latest = {}
            for event, (sid, ts) in events.items():
                if sid not in latest or ts > events[latest[sid]][1]:
                    latest[sid] = event
            for sid, ts in hints.items():
                if sid not in latest:
                    self.add(table, name, ("invocation", sid), sid, ts)
                elif ts > events[latest[sid]][1]:
                    events[latest[sid]] = sid, ts
        self.hints.clear()

    def report(self):
        self.flush_invocations()
        result = {}
        for table, groups in self.tables.items():
            result[table] = {}
            for name, events in groups.items():
                sessions = {s for s, _ in events.values() if s}
                latest = max(ts for _, ts in events.values())
                result[table][name] = {
                    "events": len(events), "sessions": len(sessions),
                    "last": datetime.fromtimestamp(latest, self.tz).date().isoformat(),
                }
        days = sorted(self.observed)
        if not self.sources:
            status = "unavailable"
        elif (self.issues or not days or
              (not self.earlier and days[0] > datetime.fromtimestamp(self.start, self.tz).date().isoformat())):
            status = "partial"
        else:
            status = "observed"
        result["ambiguous_native"] = self.ambiguous_native
        result["ambiguous_invocation"] = {k:v for k,v in self.ambiguous_invocation.items()
                                          if k not in result["skills"]}
        result["coverage"] = {
            "status": status, "sources": sorted(self.sources), "issues": dict(self.issues),
            "days_with_activity": len(days), "blind_spots": self.blind_spots, "first": days[0] if days else None,
            "last": days[-1] if days else None,
        }
        return result


class _Paths:
    """Recognize registered roots and real paths of currently installed symlinks."""
    def __init__(self, home, client, agents_root=None):
        self.home = home.expanduser().absolute()
        self.client = client
        default = Path.home() / ("." + client)
        installed_default = self.home.resolve() == default.resolve()
        homes = {self.home, self.home.resolve()}
        if installed_default:
            homes.add(default)
        roots = [h / "skills" for h in homes]
        if client == "codex":
            roots += [Path(agents_root).expanduser().absolute() if agents_root is not None else Path.home() / ".agents" / "skills"]
        self.roots = {p for r in roots for p in (r, r.resolve())}
        self.caches = {h / "plugins/cache" for h in homes}
        self.aliases = defaultdict(set)
        for root in self.roots:
            try:
                for skill in root.iterdir():
                    if skill.is_symlink() and (skill / "SKILL.md").is_file():
                        self.aliases[skill.resolve()].add(skill.name)
            except OSError:
                pass

    def identify(self, raw, cwd="", script=False):
        if not isinstance(raw, str) or not raw or "\x00" in raw:
            return None, None, None
        if raw.startswith("$HOME/"):
            raw = "~/" + raw[6:]
        try:
            p = Path(raw).expanduser()
            if not p.is_absolute():
                if not isinstance(cwd, str) or not Path(cwd).is_absolute():
                    return None, None, None
                p = Path(cwd) / p
            p = Path(os.path.normpath(p))
        except (OSError, RuntimeError, ValueError):
            return None, None, None
        if script:
            if "scripts" not in p.parts:
                return None, None, None
            root = Path(*p.parts[:p.parts.index("scripts")])
        else:
            if p.name != "SKILL.md":
                return None, None, None
            root = p.parent
        for cache in self.caches:
            if root.is_relative_to(cache):
                parts = root.relative_to(cache).parts
                if len(parts) == 5 and parts[3] == "skills":
                    return parts[1] + ":" + parts[4], parts[1], root / "SKILL.md"
                if script and len(parts) == 3:
                    return None, parts[1], None
        for r in self.roots:
            if root.is_relative_to(r):
                parts = root.relative_to(r).parts
                if len(parts) == 1 or (len(parts) == 2 and parts[0] == ".system"):
                    return parts[-1], None, root / "SKILL.md"
                if self.client == "claude" and len(parts) == 3:
                    if parts[0] == "synced":
                        return "anthropic-skills:" + parts[-1], None, root / "SKILL.md"
                    if parts[1] == "skills":
                        return parts[0] + ":" + parts[2], parts[0], root / "SKILL.md"
        aliases = self.aliases.get(root, set())
        if len(aliases) == 1:
            return next(iter(aliases)), None, root / "SKILL.md"
        # A project entry is only attributable to its path. Another repository (or
        # a global install) may have a distinct skill with the same name.
        if root.parent.name == "skills" and root.parent.parent.name in (
                (".agents", ".codex") if self.client == "codex" else (".claude",)):
            return None, None, root / "SKILL.md"
        return None, None, None


def _files(root, glob, ev):
    try:
        return sorted(root.rglob(glob)) if root.is_dir() else []
    except OSError:
        ev.issues["inaccessible_directory"] += 1
        return []


def _lines(path, ev):
    try:
        with path.open("rb") as f:
            while raw := f.readline(MAX_LINE):
                if len(raw) == MAX_LINE and not raw.endswith(b"\n"):
                    while raw and not raw.endswith(b"\n"):
                        raw = f.readline(MAX_LINE)
                    ev.issues["oversized_record"] += 1
                    continue
                if not raw.strip():
                    continue
                record = _parse(raw)
                if not record:
                    ev.issues["invalid_record"] += 1
                    continue
                yield record
    except OSError:
        ev.issues["unreadable_file"] += 1


def _recent(path, ev):
    try:
        return path.stat().st_mtime >= ev.start
    except OSError:
        ev.issues["unreadable_file"] += 1
        return False


def _slash_envelope(text, known_names):
    # Only accept the client's complete command-message / command-name envelope,
    # not ordinary prose, /strings or quoted snippets. Built-in commands without
    # a matching installed skill are not evidence.
    if (not isinstance(text, str) or len(text) > 8192
            or not text.startswith(("<command-name>", "<command-message>"))
            or "<!" in text or "<?" in text):
        return None
    try:
        root = ET.fromstring("<root>" + text + "</root>")
    except ET.ParseError:
        return None
    tags = [x.tag for x in root]
    if (set(tags) not in ({"command-name", "command-message"},
                          {"command-name", "command-message", "command-args"})
            or len(set(tags)) != len(tags) or any(
                len(x) or x.attrib or (x.tail or "").strip() for x in root)):
        return None
    name = (root.findtext("command-name") or "").strip().lstrip("/")
    return name if name in known_names else None


def _selected(content, ev, paths, session, ts, cwd):
    if not isinstance(content, list):
        return
    for user_input in content:
        b = _object(user_input)
        if b.get("type") != "skill" or not isinstance(b.get("name"), str) or not isinstance(b.get("path"), str):
            continue
        # Trust a typed selection only to the extent that its path can be scoped.
        name, _, path = paths.identify(b["path"], cwd)
        if path:
            ev.invocation(name, session, ts, path)
        elif NAME.fullmatch(b["name"]):
            # A relative/orchestrator path may not identify a registered local copy.
            day = datetime.fromtimestamp(ts, ev.tz).date().isoformat()
            ev.ambiguous_invocation[b["name"]] = max(day, ev.ambiguous_invocation.get(b["name"], day))


def _claude(home, ev):
    paths = _Paths(home, "claude")
    ev.blind_spots.append("claude_direct_invocation_markers_vary_by_version")
    known_names = set(ev.known_paths.values())
    for file in _files(home / "projects", "*.jsonl", ev):
        if not _recent(file, ev):
            continue
        calls, results = {}, {}
        for record in _lines(file, ev):
            session = record.get("sessionId")
            ts = _time(record.get("timestamp"))
            if not isinstance(session, str) or record.get("type") not in ("user", "assistant", "attachment"):
                continue
            if record.get("type") == "attachment":
                if ts is None or session in ev.excluded or not ev.start <= ts <= ev.end:
                    continue
                att = _object(record.get("attachment"))
                # Compaction can re-list a skill invoked before this retained window.
                # Its timestamp protects the row from a confident zero, not a use count.
                if att.get("type") == "invoked_skills" and isinstance(att.get("skills"), list):
                    for sk in att["skills"]:
                        name = _object(sk).get("name")
                        if isinstance(name, str) and NAME.fullmatch(name):
                            day = datetime.fromtimestamp(ts, ev.tz).date().isoformat()
                            ev.ambiguous_invocation[name] = max(day, ev.ambiguous_invocation.get(name, day))
                continue
            if ts is not None:
                ev.sources.add("claude_transcripts")
            if not ev.activity(session, ts):
                continue
            msg = _object(record.get("message"))
            blocks = msg.get("content")
            if record["type"] == "user" and isinstance(blocks, str):
                slash = _slash_envelope(blocks, known_names)
                if slash:
                    ev.invocation(slash, session, ts)
            if not isinstance(blocks, list):
                continue
            for b in blocks:
                b = _object(b)
                if record["type"] == "user" and b.get("type") == "text":
                    txt = b.get("text")
                    if isinstance(txt, str):
                        slash = _slash_envelope(txt, known_names)
                        if slash:
                            ev.invocation(slash, session, ts)
                        if record.get("isMeta") is True and txt.startswith("Base directory for this skill: "):
                            directory = txt.split("\n", 1)[0].partition(": ")[2].strip()
                            n, _, p = paths.identify(str(Path(directory)/"SKILL.md"), record.get("cwd", ""))
                            if n or p:
                                ev.invocation(n, session, ts, p)
                if record["type"] == "user" and b.get("type") == "tool_result":
                    ident = b.get("tool_use_id")
                    if isinstance(ident, str):
                        results[(session, ident)] = not b.get("is_error", False)
                if record["type"] != "assistant" or b.get("type") != "tool_use":
                    continue
                ident = b.get("id")
                if not isinstance(ident, str) or not ident:
                    continue
                args = _object(b.get("input"))
                if b.get("name") == "Skill" and isinstance(args.get("skill"), str):
                    n = args["skill"].lstrip("/")
                    if NAME.fullmatch(n):
                        calls[(session, ident)] = n, None, ts
                elif b.get("name") == "Read":
                    n, _, p = paths.identify(args.get("file_path"), record.get("cwd", ""))
                    if n or p:
                        calls[(session, ident)] = n, p, ts
        for (session, ident), (name, path, ts) in calls.items():
            if results.get((session, ident)):
                ev.skill(name, ident, session, ts, path)
    ev.flush_invocations()
    # Native lastUsedAt proves at least one use, never the entire all-time usageCount.
    # It has no session id. With exclusions it can only rule out a confident zero.
    for file in [home / ".claude.json"] + ([home.parent / ".claude.json"] if home.name == ".claude" else []):
        if not file.is_file():
            continue
        try:
            with file.open("rb") as f:
                data = _parse(f.read(MAX_LINE))
        except OSError:
            ev.issues["unreadable_native_state"] += 1
            continue
        native = data.get("skillUsage")
        if not isinstance(native, dict):
            continue
        ev.sources.add("claude_native_last_used")
        for name, row in native.items():
            ts = _time(_object(row).get("lastUsedAt"))
            if not NAME.fullmatch(name) or ts is None or not ev.start <= ts <= ev.end:
                continue
            if ev.excluded:
                if not ev.tables["skills"].get(name):
                    ev.ambiguous_native[name] = datetime.fromtimestamp(ts, ev.tz).date().isoformat()
                continue
            for table, key in [("skills", name), ("plugins", name.split(":")[0])]:
                if table == "plugins" and (":" not in name or name.startswith("anthropic-skills:")):
                    continue
                events = ev.tables[table][key]
                if not events:
                    ev.add(table, key, "native:last", "", ts)
                else:
                    # Keep the verified floor while updating the most recent evidence date.
                    latest = max(events, key=lambda e: events[e][1])
                    if ts > events[latest][1]:
                        events[latest] = (events[latest][0], ts)
        break


def _simple_operands(command):
    """Only standalone shell commands; compound commands have ambiguous exit codes."""
    if not isinstance(command, str) or len(command) > 32000:
        return []
    try:
        words = shlex.split(command)
        if len(words) == 3 and Path(words[0]).name in {"sh", "bash", "zsh"} and words[1] in {"-c", "-lc"}:
            command = words[2]
            words = shlex.split(command)
    except ValueError:
        return []
    if not words or any(c in command for c in "\n;&|<>\x60") or "$(" in command:
        return []
    binary = Path(words[0]).name
    if binary in {"cat", "head", "tail", "nl", "sed"}:
        return [(w, False) for w in words[1:] if w.endswith("SKILL.md")]
    if binary in {"python", "python3", "bash", "sh", "zsh", "node", "ruby"} and len(words) >= 2:
        return [(words[1], True)] if not words[1].startswith("-") else []
    return [(words[0], True)] if "/" in words[0] else []


def _operands(command):
    if not isinstance(command, str) or len(command) > 32000:
        return []
    try:
        wrapped = shlex.split(command)
        if len(wrapped) == 3 and Path(wrapped[0]).name in {"sh", "bash", "zsh"} and wrapped[1] in {"-c", "-lc"}:
            command = wrapped[2]
    except ValueError:
        return []
    # A literal && chain guarantees each stage was successful if the shell exited 0.
    # Use lexical tokens rather than splitting quoted strings that happen to contain &&.
    if "&&" not in command:
        return _simple_operands(command)
    if any(c in command for c in "\n;|<>\x60()") or "||" in command:
        return []
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="&")
        lexer.whitespace_split = True
        lexer.commenters = ""
        words = list(lexer)
    except ValueError:
        return []
    # Detect quoted/control masquerading as an operator: re-quoting shlex tokens
    # loses that distinction, so only handle unquoted chain text in this branch.
    if '"' in command or "'" in command:
        return []
    result, stage = [], []
    for w in words + ["&&"]:
        if w == "&&":
            if not stage or stage[0] in {"if", "then", "else", "while", "for", "!", "exit", "return"}:
                return []
            result.extend(_simple_operands(shlex.join(stage)))
            stage = []
        elif w == "&":
            return []
        else:
            stage.append(w)
    return result


def _app_owners(paths):
    """Map tool namespaces to an unambiguous package using local plugin app manifests."""
    candidates = defaultdict(set)
    for cache in {c.resolve() for c in paths.caches}:
        for file in cache.glob("*/*/*/.app.json"):
            package = file.parents[1].name
            try:
                with file.open("rb") as f:
                    apps = _object(_parse(f.read(256 * 1024)).get("apps"))
            except OSError:
                continue
            for key, app in apps.items():
                candidates[key.replace("-", "_")].add(package)
                app_id = _object(app).get("id", "")
                if isinstance(app_id, str) and app_id.startswith("connector_openai_"):
                    candidates[app_id.removeprefix("connector_openai_")].add(package)
    aliases = {"chatgpt_space": "pages", "pets": "chatgpt_pets"}
    for name, original in aliases.items():
        candidates[name].update(candidates.get(original, set()))
    return {n:next(iter(p)) for n, p in candidates.items() if len(p) == 1}


def _command(ev, paths, item, event, session, ts):
    if item.get("status") != "completed" or item.get("exitCode") != 0:
        return
    command = item.get("command")
    operands = _operands(command)
    # A successful structured read classification also covers readers added by a
    # newer client. Reject shell constructs that can mask failed/untaken stages.
    standalone = not command or (isinstance(command, str) and not re.search(
        r"[;&|<>\n`]|\$\(|(?:^|\s)(?:if|for|while|exit|return|!)(?:\s|$)", command.replace("&&"," ")))
    if standalone and isinstance(item.get("commandActions"), list):
        operands.extend((a.get("path"),False) for a in item["commandActions"]
                        if isinstance(a,dict) and a.get("type") == "read")
    for raw, script in operands:
        name, plugin, path = paths.identify(raw, item.get("cwd", ""), script)
        if name or path:
            ev.skill(name, event, session, ts, path)
        elif plugin:
            ev.add("plugins", plugin, event, session, ts)


def _projected(dbfile, ev, paths):
    apps = _app_owners(paths)
    with closing(sqlite3.connect(dbfile.absolute().as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("SELECT thread_id,item_id,item_type,created_at_ms,item_json FROM thread_items LIMIT 0")
        start, end = round(ev.start * 1000), int(ev.end * 1000)
        stats = db.execute("""SELECT MIN(created_at_ms),MAX(created_at_ms) FROM thread_items
                              WHERE item_type IN ('agentMessage','userMessage','commandExecution','mcpToolCall')""").fetchone()
        if stats[0] is None:
            return False
        ev.sources.add("codex_thread_projection")
        ev.earlier = stats[0] < start
        query = """SELECT thread_id,item_id,item_type,created_at_ms,
                          CASE WHEN item_type != 'agentMessage' THEN item_json END
                   FROM thread_items WHERE created_at_ms BETWEEN ? AND ?
                   AND item_type IN ('agentMessage','userMessage','commandExecution','mcpToolCall','dynamicToolCall')"""
        for session, event, kind, tm, raw in db.execute(query, (start, end)):
            ev.projected_sessions.add(session)
            if not ev.activity(session, tm / 1000) or not raw:
                continue
            item = _parse(raw)
            if not item:
                ev.issues["invalid_record"] += 1
            elif kind == "userMessage":
                _selected(item.get("content"), ev, paths, session, tm / 1000, item.get("cwd", ""))
            elif kind == "commandExecution":
                _command(ev, paths, item, event, session, tm / 1000)
            elif item.get("status") == "completed" and not item.get("error") and item.get("success") is not False:
                pid = item.get("pluginId")
                if isinstance(pid, str) and pid:
                    ev.add("plugins", pid.split("@")[0], event, session, tm / 1000)
                elif item.get("server") == "codex_apps" and isinstance(item.get("tool"), str):
                    namespace, sep, _ = item["tool"].partition(".")
                    if sep and namespace in apps:
                        ev.add("plugins", apps[namespace], event, session, tm / 1000)
        return True


def _rollout(file, ev, paths):
    session = None
    cwd = ""
    pending = {}
    for record in _lines(file, ev):
        typ, body = record.get("type"), _object(record.get("payload"))
        if typ == "session_meta":
            session, cwd = body.get("id"), body.get("cwd", "")
            if not isinstance(session, str) or session in ev.excluded or session in ev.projected_sessions:
                return
            if isinstance(session, str):
                ev.sources.add("codex_rollouts")
            continue
        if not isinstance(session, str):
            continue
        ts = _time(record.get("timestamp"))
        if not ev.activity(session, ts):
            continue
        if typ == "response_item" and body.get("type") == "message" and body.get("role") == "user":
            _selected(body.get("content"), ev, paths, session, ts, cwd)
        if typ == "turn_context" and isinstance(body.get("cwd"), str):
            cwd = body["cwd"]
        if typ != "response_item":
            continue
        call = body.get("call_id")
        if not isinstance(call, str) or not call:
            continue
        item_type = body.get("type")
        if item_type == "function_call" and body.get("name") in {"exec_command", "functions.exec_command", "shell"}:
            args = _parse(body.get("arguments")) if isinstance(body.get("arguments"), str) else _object(body.get("arguments"))
            command = args.get("cmd") or args.get("command")
            if isinstance(command, list) and all(isinstance(t, str) for t in command):
                command = shlex.join(command)
            if isinstance(command, str):
                pending[call] = command, args.get("workdir") or cwd, ts
        elif item_type == "function_call_output" and call in pending:
            output = body.get("output", "")
            if not isinstance(output, str):
                continue
            structured = _parse(output)
            meta = _object(structured.get("metadata"))
            exit_code = structured.get("exit_code", meta.get("exit_code"))
            if exit_code is None:
                # Only inspect the tool envelope, never strings in the command's output.
                header = output.partition("Output:")[0][:512]
                ok = re.match(r"\A(?:Chunk ID: [^\n]*\n)?Wall time: [^\n]*\nProcess exited with code 0(?:\n|$)", header)
            else:
                ok = isinstance(exit_code, int) and not isinstance(exit_code, bool) and exit_code == 0
            command, workdir, called_at = pending.pop(call)
            if ok:
                _command(ev, paths, {"command": command, "cwd": workdir, "status": "completed",
                                      "exitCode": 0}, call, session, called_at)


def _codex(home, ev, agents_root=None):
    ev.blind_spots.append("codex_remote_and_direct_invocation_markers_vary_by_version")
    paths = _Paths(home, "codex", agents_root)
    # Prefer the installed projection, then read only unprojected sessions from
    # JSONL. The same action can use different IDs between the two formats.
    for dbfile in sorted(home.glob("thread_history_*.sqlite"), key=lambda p: int(p.stem.split("_")[-1])
                         if p.stem.split("_")[-1].isdigit() else -1, reverse=True):
        try:
            if _projected(dbfile, ev, paths):
                break
        except (sqlite3.Error, OSError):
            ev.issues["unsupported_or_unreadable_projection"] += 1
    for folder in ("sessions", "archived_sessions"):
        for p in _files(home / folder, "rollout-*.jsonl*", ev):
            if not _recent(p, ev):
                continue
            uuid = re.search(r"([a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12})\.jsonl", p.name)
            if uuid and (uuid[1] in ev.projected_sessions or uuid[1] in ev.excluded):
                continue
            if p.suffix != ".jsonl":
                ev.issues["compressed_or_unknown_rollout_skipped"] += 1
                continue
            _rollout(p, ev, paths)


def collect(claude_home, codex_home, days, now, exclude_ids=(), *, clients=("claude", "codex"), agents_root=None, known_paths=None):
    """Aggregate the selected local calendar days through an aware cutoff, inclusive.

    Sources: Claude transcripts (matching successful Skill/Read returns) and
    optional latest native usage; Codex SQLite projection, or plaintext rollout
    logs on older installations. Other actions, third-party/remote tools without
    attribution, compressed-only legacy logs and manually opened docs can be missed.
    Zeros mean no supported evidence in retained logs. Coverage is per client.
    known_paths optionally maps a client to its exact canonical SKILL.md -> name
    inventory. A single-client caller may pass its flat inventory directly.
    Never associate a different historical project's same-name file by basename.
    """
    if not isinstance(days, int) or isinstance(days, bool) or days < 1:
        raise ValueError("days must be a positive integer")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be a timezone-aware datetime")
    start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    excluded = set(exclude_ids or ())
    result = {}
    clients = {clients} if isinstance(clients, str) else set(clients)
    if not clients <= {"claude", "codex"}:
        raise ValueError("unrecognized client")
    for name, home, run in [("claude", claude_home, _claude), ("codex", codex_home, _codex)]:
        if name not in clients:
            continue
        lookup = (known_paths or {}).get(name)
        if lookup is None and len(clients) == 1:
            lookup = known_paths
        ev = _Evidence(start, now, excluded, {
            str(p): n for p, n in (lookup or {}).items()
            if isinstance(n, str) and NAME.fullmatch(n) and Path(p).is_absolute()
        })
        if name == "codex":
            run(Path(home).expanduser(), ev, agents_root)
        else:
            run(Path(home).expanduser(), ev)
        result[name] = ev.report()
    return result
