"""Read discoverable skills, effective client catalogs and their control identifiers."""
import json
import os
import queue
import shutil
import subprocess
import threading
import tomllib
from pathlib import Path


def load_config(path):
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8-sig")
    value = tomllib.loads(raw) if path.suffix == ".toml" else json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("配置文件根节点必须为对象")
    return value


def protocol(argv, requests, decode, env, cwd, timeout):
    """Wait for each reply before sending the next request. Submit no model turn."""
    output = queue.Queue()
    with subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True, encoding="utf-8", errors="replace") as proc:
        def exchange():
            try:
                last = None
                for key, request in requests:
                    proc.stdin.write(json.dumps(request) + "\n")
                    proc.stdin.flush()
                    for line in proc.stdout:
                        try:
                            message = json.loads(line)
                        except ValueError:
                            continue
                        reply = decode(message, key)
                        if reply is not None:
                            last = reply
                            break
                    else:
                        raise ValueError("接口提前退出")
                output.put((True, last))
            except Exception as exc:
                output.put((False, exc))
        worker = threading.Thread(target=exchange, daemon=True)
        worker.start()
        try:
            ok, value = output.get(timeout=timeout)
            if not ok:
                raise value
            return value
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            worker.join(timeout=2)


def live_skills(client, exe, env, cwd, timeout):
    if client == "codex":
        reqs = [(1, "initialize", {"clientInfo": {"name": "skill_loader_audit", "version": "1"},
                                   "capabilities": {"experimentalApi": True}}),
                (2, "skills/list", {"cwds": [str(cwd)], "forceReload": True})]
        def decode(msg, key):
            if msg.get("id") == key:
                if "error" in msg:
                    raise ValueError("客户端技能接口不可用")
                return msg["result"]
        result = protocol([exe, "app-server"], [(i, {"id": i, "method": method, "params": params})
                          for i, method, params in reqs], decode, env, cwd, timeout)
        data = result["data"][0]
        return data["skills"], bool(data.get("errors"))
    reqs = [(k, {"type": "control_request", "request_id": k, "request": {"subtype": k}})
            for k in ("initialize", "get_context_usage")]
    def decode(msg, key):
        rep = msg.get("response", {})
        if msg.get("type") == "control_response" and rep.get("request_id") == key:
            if rep.get("subtype") != "success":
                raise ValueError("上下文接口不可用")
            return rep.get("response", {})
    argv = [exe, "-p", "--verbose", "--input-format", "stream-json", "--output-format",
            "stream-json", "--no-session-persistence", "--strict-mcp-config"]
    result = protocol(argv, reqs, decode, env, cwd, timeout)
    return result["skills"]["skillFrontmatter"], False


def discovered_name(file):
    # Skill metadata commonly uses plain/quoted scalar names. Fall back to its directory.
    with file.open(encoding="utf-8-sig", errors="replace") as stream:
        text = stream.read(16384).splitlines()
    if text and text[0].strip() == "---":
        for line in text[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                name = line.partition(":")[2].strip().strip("\"'")
                if name and all(c.isalnum() or c in "-_." for c in name):
                    return name
    return file.parent.name


def inventory(client, home, cwd, live=True, timeout=20, agents_root=None):
    notes = []
    config = load_config(home / ("config.toml" if client == "codex" else "settings.json"))
    controls = config.get("skillOverrides", {}) if client == "claude" else {}
    configs = config.get("skills", {}).get("config", []) if client == "codex" else []
    rows = {}
    def canonical(p):
        return str(Path(p).expanduser().resolve()) if p else ""
    def disabled(name, path):
        if client == "claude":
            return controls.get(name) == "off"
        enabled=True
        for s in configs:
            if s.get("name") == name:
                enabled=s.get("enabled",True)
            if s.get("path") and path:
                cfgpath = Path(s["path"]).expanduser()
                if cfgpath.name != "SKILL.md":
                    cfgpath = cfgpath / "SKILL.md"
                if canonical(cfgpath) == path:
                    enabled=s.get("enabled",True)
        return not enabled
    def add(name, p, source, state=None, plugin=None):
        path = canonical(p)
        state = state or ("disabled" if disabled(name, path) else "candidate")
        key = (name, path)
        rows[key] = {"client": client, "name": name, "path": path or None, "source": source,
                     "state": state, "plugin": plugin}
    roots = [(home/"skills", "user")]
    if client == "codex":
        personal = Path.home()
        roots += [(home/"skills"/".system", "system"), ((agents_root or personal/".agents"/"skills"), "shared")]
    project_roots = [cwd]
    for parent in cwd.parents:
        if (project_roots[-1]/".git").exists() or parent == Path.home() or parent == parent.parent:
            break
        project_roots.append(parent)
    for root in project_roots:
        roots.append((root/(".agents" if client=="codex" else ".claude")/"skills","project"))
    for root, source in roots:
        for file in sorted(root.glob("*/SKILL.md")):
            if file.is_file():
                add(discovered_name(file), file, source)
    if client == "claude":
        for file in (home/"skills"/"synced").glob("*/*/SKILL.md"):
            add("anthropic-skills:"+discovered_name(file), file, "synced")
        for name, mode in controls.items():
            if mode == "off" and not any(r["name"]==name for r in rows.values()):
                add(name,None,"override","disabled")
    else:
        for s in configs:
            p = s.get("path")
            if not p or s.get("enabled",True):
                continue
            file = Path(p).expanduser()
            if file.name != "SKILL.md":
                file = file/"SKILL.md"
            if not any(r["path"] == canonical(file) for r in rows.values()):
                add(file.parent.name,file,"override","disabled")
    exe = shutil.which(client) if live else None
    verified = False
    if exe:
        env = dict(os.environ)
        env_key="CODEX_HOME" if client=="codex" else "CLAUDE_CONFIG_DIR"
        default=(Path.home()/("."+client)).resolve()
        if env_key in env or home.resolve()!=default:
            if env_key not in env or Path(env[env_key]).expanduser().resolve()!=home.resolve():
                env[env_key]=str(home)
        try:
            skills, partial = live_skills(client, exe, env, cwd, timeout)
            for item in skills:
                name = item["name"]
                if item.get("source") == "syncedSkills" and ":" not in name:
                    name = "anthropic-skills:"+name
                path = canonical(item.get("path"))
                # Replace provisional disk names with the runtime namespace for the same file.
                if path:
                    for k in [k for k in rows if k[1]==path]:
                        rows.pop(k)
                rows.pop((name, ""), None)
                add(name,path,item.get("source",item.get("scope","client")),
                    "loaded" if item.get("enabled",True) else "disabled",
                    item.get("pluginName") or (item.get("pluginId") or "").split("@")[0] or None)
            verified = True
            if partial:
                notes.append("客户端报告部分技能目录读取失败。")
        except (OSError, ValueError, KeyError, IndexError, TypeError, queue.Empty):
            notes.append("客户端接口不可用或超时，仅列出能从文件确认的配置。")
    elif live:
        notes.append("未找到客户端可执行文件，仅检查本地文件。")
    if exe and client == "codex":
        try:
            proc=subprocess.run([exe,"plugin","list","--json"],cwd=cwd,env=env,timeout=timeout,
                                capture_output=True,check=True)
            installs=json.loads(proc.stdout)["installed"]
            for plug in installs:
                name, market, version = plug["name"], plug["marketplaceName"], plug.get("version")
                if not version or not plug.get("enabled") or not config.get("plugins",{}).get(plug["pluginId"],{}).get("enabled",True):
                    continue
                # Enumerate the selected version only. A cached older version may never have been loaded.
                if any(Path(t).name!=t or t in ("",".","..") for t in (name,market,version)):
                    continue
                source_root=home/"plugins"/"cache"/market/name/version/"skills"
                known_paths={r["path"] for r in rows.values() if r["state"]=="loaded"}
                for skill in sorted(source_root.glob("*/SKILL.md")):
                    if not skill.is_file() or canonical(skill) in known_paths:
                        continue
                    qualified=name+":"+discovered_name(skill)
                    # Remove a disabled config stub if its path matches this registered plugin.
                    rows.pop((skill.parent.name,canonical(skill)),None)
                    add(qualified,skill,"plugin-package",plugin=name)
        except (OSError,KeyError,ValueError,TypeError,subprocess.SubprocessError):
            notes.append("当前版本没有提供可核对的插件包清单。")
    return {"client":client,"live":verified,"notes":notes,
            "items":sorted(rows.values(),key=lambda r:(r["name"],r["path"] or ""))}
