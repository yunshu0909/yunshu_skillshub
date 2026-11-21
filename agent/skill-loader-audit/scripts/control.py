"""Preview and reversibly change per-user skill overrides (Python 3.11+).

The caller supplies the current inventory and obtains the user's approval for
the displayed plan before apply_plan. Receipts contain selectors and override
states only. No skill directories, plugins, hooks, or shared sources are moved.
"""
import copy
import hashlib
import json
import os
from contextlib import ExitStack, contextmanager
from pathlib import Path
import re
import stat
import tempfile
import tomllib


class ControlError(ValueError):
    pass


def _require(test, message):
    if not test:
        raise ControlError(message)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "Duplicate JSON key in configuration")
        result[key] = value
    return result


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _digest(obj):
    stable = json.dumps(obj, sort_keys=True, ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(stable.encode()).hexdigest()


def _read(path):
    try:
        _require(path.stat().st_nlink == 1 and path.is_file(), "Expected a regular, non-hardlinked config file")
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _fingerprint(raw):
    return None if raw is None else hashlib.sha256(raw).hexdigest()


def _parse(client, raw):
    if raw is None:
        return {}
    s = raw.decode("utf-8-sig")
    if client == "codex":
        return tomllib.loads(s)
    data = json.loads(s, object_pairs_hook=_unique)
    _require(isinstance(data, dict), "Expected JSON settings object")
    return data


def _paths(claude_home, codex_home):
    return {"claude": Path(claude_home).expanduser().absolute() / "settings.json",
            "codex": Path(codex_home).expanduser().absolute() / "config.toml"}


def _identity(row):
    client = row["client"]
    if client == "claude":
        name = row["name"]
        _require(isinstance(name, str) and name.strip() == name and name
                 and not any(ord(c) < 32 for c in name), "Invalid Claude skill name")
        return client, name
    _require(client == "codex", "Unknown client")
    path = Path(row["path"])
    _require(path.is_absolute() and path.name == "SKILL.md", "Expected absolute path to SKILL.md")
    return client, str(path.resolve())


def _known_inventory(inventory):
    known = {}
    for row in inventory:
        if row.get("client") == "codex" and not row.get("path"):
            continue  # Remote/conditional entry with no configurable path.
        key = _identity(row)
        known.setdefault(key, set()).add(row.get("path") or "")
    return known


def _select(known, key):
    _require(key in known, "Target is absent from the current inventory")
    _require(key[0] != "claude" or len(known[key]) == 1,
             "Ambiguous Claude name: a name-based override would affect multiple entries")


def _codex_rows(doc):
    rows = doc.get("skills", {}).get("config", [])
    _require(isinstance(rows, list) and all(isinstance(r, dict) for r in rows), "Unsupported skills.config format")
    return rows


def _matches(rule, selector):
    path = rule.get("path")
    if not isinstance(path, str):
        return False
    p = Path(path).expanduser()
    if not p.is_absolute():
        return False
    target = p if p.name == "SKILL.md" else p / "SKILL.md"
    return target.resolve() == Path(selector)


def _check_rule_order(doc, selector, names, enabled):
    # Codex gives the last matching name or path rule precedence. Never flip
    # an earlier path flag if a later name rule would hide the change.
    last_path = None
    final = None
    for i, rule in enumerate(_codex_rows(doc)):
        if _matches(rule, selector):
            last_path = i
            final = None
        elif last_path is not None and rule.get("name") in names:
            final = rule.get("enabled", True)
    _require(final is None or final == enabled,
             "A later name-based rule overrides this existing path; inspect the rule order first")


def _snapshot(client, doc, selector):
    if client == "claude":
        cfg = doc.get("skillOverrides", {})
        _require(isinstance(cfg, dict), "Expected skillOverrides object")
        if selector not in cfg:
            return {"exists": False}
        value = cfg[selector]
        _require(value in ("on", "off"), "Unsupported preexisting Claude override")
        return {"exists": True, "enabled": value == "on"}
    matches = [r for r in _codex_rows(doc) if _matches(r, selector)]
    _require(len(matches) <= 1, "Multiple Codex rules select the same file")
    if not matches:
        return {"exists": False}
    row = matches[0]
    _require(set(row) <= {"path", "enabled"}, "Unsupported mixed Codex rule")
    if "enabled" in row:
        _require(type(row["enabled"]) is bool, "Expected Boolean Codex override")
    return {"exists": True, "enabled": row.get("enabled")}


HEADER = re.compile(r'(?m)^[ \t]*\[\[[ \t]*skills[ \t]*\.[ \t]*config[ \t]*\]\][ \t]*(?:#[^\r\n]*)?(?=\r?$)')
NEXT = re.compile(r'(?m)^[ \t]*\[')
ENABLED = re.compile(r'(?m)^([ \t]*enabled[ \t]*=[ \t]*)(true|false)([ \t]*(?:#[^\r\n]*)?)(\r?$)')
PATH_LINE = re.compile(r'(?m)^[ \t]*path[ \t]*=[^\n]*(?:\n|$)')


def _without_empty_tables(doc):
    doc = copy.deepcopy(doc)
    if "skills" in doc:
        if doc["skills"].get("config") == []:
            del doc["skills"]["config"]
        if not doc["skills"]:
            del doc["skills"]
    return doc


def _new_stanza(selector, enabled, eol):
    path_line = "path = " + json.dumps(selector, ensure_ascii=False)
    enabled_line = "enabled = " + ("true" if enabled else "false")
    return eol + eol.join(("[[skills.config]]", path_line, enabled_line, ""))


def _edit_toml(s, selector, desired):
    doc = tomllib.loads(s)
    result = copy.deepcopy(doc)
    rows = result.setdefault("skills", {}).setdefault("config", [])
    row = next((r for r in rows if _matches(r, selector)), None)
    eol = "\r\n" if "\r\n" in s else "\n"
    val = desired.get("enabled")
    literal = "true" if val else "false"
    if row is None:
        _require(desired["exists"] and type(val) is bool, "Cannot create incomplete rule")
        rows.append({"path": selector, "enabled": val})
        out = s + _new_stanza(selector, val, eol)
    else:
        if not desired["exists"]:
            rows.remove(row)
        elif val is None:
            row.pop("enabled", None)
        else:
            row["enabled"] = val
        # Parse individual standard override blocks. After the surgical edit,
        # parse the entire file and compare all keys to reject a false match
        # such as TOML-looking text inside a multiline string.
        out = None
        for h in HEADER.finditer(s):
            follow = NEXT.search(s, h.end())
            stop = follow.start() if follow else len(s)
            body = s[h.end():stop]
            try:
                contents = tomllib.loads(body)
            except tomllib.TOMLDecodeError:
                continue
            if not _matches(contents, selector):
                continue
            if not desired["exists"]:
                _require(set(contents) <= {"enabled", "path"}, "Cannot remove extended rule")
                # Undo precisely our appended stanza, including its framing
                # newline. Keep a separator if a newer table follows a file
                # that originally had no final newline.
                stanza = _new_stanza(selector, contents.get("enabled"), eol)
                start = h.start() - len(eol)
                if start >= 0 and s.startswith(stanza, start):
                    left = s[:start]
                    right = s[start + len(stanza):]
                    joiner = eol if left and not left.endswith("\n") and right and not right.startswith(("\r", "\n")) else ""
                    candidate = left + joiner + right
                else:
                    rest = PATH_LINE.sub("", ENABLED.sub("", body))
                    candidate = s[:h.start()] + rest + s[stop:]
            elif "enabled" not in contents:
                candidate = s[:h.end()] + eol + "enabled = " + literal + body + s[stop:]
            elif val is None:
                inserted = re.match(r"\r?\nenabled = (?:true|false)(?=\r?\n|$)", body)
                remaining = body[inserted.end():] if inserted else ENABLED.sub("", body)
                candidate = s[:h.end()] + remaining + s[stop:]
            else:
                candidate = s[:h.end()] + ENABLED.sub(lambda m: m[1]+literal+m[3]+m[4], body) + s[stop:]
            try:
                if _without_empty_tables(tomllib.loads(candidate)) == _without_empty_tables(result):
                    out = candidate
                    break
            except tomllib.TOMLDecodeError:
                continue
        _require(out is not None, "Cannot safely edit this TOML layout; no changes applied")
    _require(_without_empty_tables(tomllib.loads(out)) == _without_empty_tables(result), "TOML edit validation failed")
    return out


def _render(client, raw, states):
    data = _parse(client, raw)
    if client == "claude":
        cfg = data.setdefault("skillOverrides", {})
        for name, desired in states:
            if desired["exists"]:
                cfg[name] = "on" if desired["enabled"] else "off"
            else:
                cfg.pop(name, None)
        out = _json(data)
    else:
        out = (raw or b"").decode("utf-8-sig")
        for path, desired in states:
            out = _edit_toml(out, path, desired)
    return (b"\xef\xbb\xbf" if raw and raw.startswith(b"\xef\xbb\xbf") else b"") + out.encode()


def make_plan(claude_home, codex_home, targets, inventory):
    """Read-only preview. Inventory entries use client + name (Claude) or absolute path (Codex)."""
    paths = _paths(claude_home, codex_home)
    inventory = list(inventory)
    sources = _known_inventory(inventory)
    seen = set()
    changes = []
    files = {}
    docs = {}
    for item in targets:
        key = _identity(item)
        client, selector = key
        _select(sources, key)
        _require(key not in seen, "Duplicate target in request")
        if client == "codex":
            _require(Path(selector).is_file(), "Target SKILL.md no longer exists")
        seen.add(key)
        enabled = item["enabled"]
        _require(type(enabled) is bool, "enabled must be a Boolean")
        if client not in docs:
            path = paths[client].resolve()
            raw = _read(path)
            docs[client] = _parse(client, raw)
            files[client] = {"path": str(path), "sha256": _fingerprint(raw),
                             "override_table_existed": ("skillOverrides" in docs[client] if client == "claude" else "skills" in docs[client])}
        if client == "codex":
            names = {r.get("name") for r in inventory if r.get("client") == "codex"
                     and r.get("path") and _identity(r) == key and r.get("name")}
            names.add(Path(selector).parent.name)
            _check_rule_order(docs[client], selector, names, enabled)
        before = _snapshot(client, docs[client], selector)
        if before != {"exists": True, "enabled": enabled}:
            changes.append({"client": client, "selector": selector, "before": before, "enabled": enabled})
    plan = {"version": 1, "files": files, "changes": changes}
    return {**plan, "id": _digest(plan)}


def _verify_plan(plan):
    body = {k: v for k, v in plan.items() if k != "id"}
    _require(plan.get("version") == 1 and plan.get("id") == _digest(body), "Corrupt or modified plan")
    _require(set(plan["files"]) <= {"claude", "codex"}, "Unexpected config target")


@contextmanager
def _lock(path):
    # Stable sidecar remains after use so cooperating processes lock one inode.
    lockpath = path.with_name("." + path.name + ".skill-loader.lock")
    _require(not lockpath.is_symlink(), "Refusing symlinked lock file")
    fd = os.open(lockpath, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "r+b") as f:
        if os.name == "nt":
            import msvcrt
            if os.fstat(f.fileno()).st_size == 0:
                f.write(b"0")
                f.flush()
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def _replace(path, expected, data):
    if data is None:
        _require(_read(path) == expected, "Concurrent configuration change")
        path.unlink()
        return
    fd, tmp = tempfile.mkstemp(prefix="."+path.name+".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            if path.exists():
                os.chmod(tmp, stat.S_IMODE(path.stat().st_mode))
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        _require(_read(path) == expected, "Concurrent configuration change")
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def _commit(edits):
    done = []
    try:
        for path, old, new in edits:
            _replace(path, old, new)
            done.append((path, old, new))
    except BaseException:
        for path, old, new in reversed(done):
            _replace(path, new, old)
        raise


def _locked_paths(stack, plan, claude_home, codex_home):
    paths = _paths(claude_home, codex_home)
    selected = {}
    for client in sorted(plan["files"]):
        expected = Path(plan["files"][client]["path"])
        target = paths[client].resolve()
        _require(target == expected and target.parent.is_dir(), "Config location changed or missing")
        stack.enter_context(_lock(target))
        selected[client] = target
    _require(len(set(selected.values())) == len(selected), "Config files alias each other")
    return selected


def apply_plan(plan, claude_home, codex_home, inventory, receipt_path):
    """Require a previously reviewed plan, a fresh inventory, and a new, unused receipt path."""
    _verify_plan(plan)
    receipt = Path(receipt_path).absolute()
    with ExitStack() as stack:
        paths = _locked_paths(stack, plan, claude_home, codex_home)
        _require(not receipt.is_symlink() and receipt.resolve() not in paths.values(), "Invalid receipt location")
        known = _known_inventory(inventory)
        edits = []
        for client, path in paths.items():
            raw = _read(path)
            _require(_fingerprint(raw) == plan["files"][client]["sha256"], "Stale preview; run plan again")
            states = []
            for change in [c for c in plan["changes"] if c["client"] == client]:
                selector = change["selector"]
                _select(known, (client, selector))
                if client == "codex":
                    _require(Path(selector).is_file(), "Target SKILL.md no longer exists")
                _require(_snapshot(client, _parse(client, raw), selector) == change["before"], "Override changed")
                states.append((selector, {"exists": True, "enabled": change["enabled"]}))
            if states:
                edits.append((path, raw, _render(client, raw, states)))
        record = {"status": "prepared", "plan": plan}
        payload = _json(record).encode()
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        _commit(edits)
        record["status"] = "applied"
        _replace(receipt, payload, _json(record).encode())
        return record


def restore(receipt_path, claude_home, codex_home):
    """Undo only this receipt's overrides, preserving unrelated config changes."""
    receipt = Path(receipt_path).absolute()
    _require(not receipt.is_symlink(), "Refusing symlinked receipt")
    receipt_raw = _read(receipt)
    _require(receipt_raw is not None, "Receipt not found")
    record = json.loads(receipt_raw)
    _require(record["status"] in ("restored", "prepared", "applied"), "Invalid receipt status")
    plan = record["plan"]
    _verify_plan(plan)
    if record["status"] == "restored":
        return record
    with ExitStack() as stack:
        paths = _locked_paths(stack, plan, claude_home, codex_home)
        _require(receipt.resolve() not in paths.values(), "Invalid receipt location")
        edits = []
        for client, path in paths.items():
            raw = _read(path)
            doc = _parse(client, raw)
            states = []
            for change in [c for c in plan["changes"] if c["client"] == client]:
                selector = change["selector"]
                current = _snapshot(client, doc, selector)
                if current == change["before"]:
                    continue
                _require(current == {"exists": True, "enabled": change["enabled"]}, "Target changed since apply; refusing to overwrite")
                states.append((selector, change["before"]))
            if not states:
                continue
            new = _render(client, raw, states)
            doc = _parse(client, new)
            previous = plan["files"][client]
            if client == "claude" and not previous["override_table_existed"] and not doc.get("skillOverrides"):
                doc.pop("skillOverrides", None)
                new = _json(doc).encode()
            if previous["sha256"] is None and not doc:
                # Only delete a newly-created file if it contains no added comments.
                if client == "claude" or not new.strip():
                    new = None
            edits.append((path, raw, new))
        _commit(edits)
        record["status"] = "restored"
        _replace(receipt, receipt_raw, _json(record).encode())
        return record
