#!/usr/bin/env python3
"""Audit local AI skill usage and manage exact per-client loading overrides."""
import argparse
import collections
from datetime import datetime
import html
import json
import os
from pathlib import Path
import sys

if sys.version_info < (3, 11):
    raise SystemExit("skill-loader-audit 需要 Python 3.11 或更新版本。")

from control import ControlError, apply_plan, make_plan, restore
from inventory import inventory
from usage import collect

CLIENTS = ("claude", "codex")
TEXT = {"loaded":"客户端列出", "disabled":"已关闭", "candidate":"目录中存在"}
NAME = {"claude":"Claude Code", "codex":"Codex"}
ZERO = {"events":0, "sessions":0, "last":None}


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--claude-home", type=Path, default=os.environ.get("CLAUDE_CONFIG_DIR") or Path.home()/".claude")
    root.add_argument("--codex-home", type=Path, default=os.environ.get("CODEX_HOME") or Path.home()/".codex")
    root.add_argument("--agents-root", type=Path, help="Shared user skills directory (normally ~/.agents/skills)")
    root.add_argument("--cwd", type=Path, default=Path.cwd(), help="Project for scope-dependent discovery")
    root.add_argument("--client", choices=(*CLIENTS, "both"), default="both")
    root.add_argument("--files-only", action="store_true", help="Skip client probes; disk candidates are unverified")
    commands = root.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="Read-only usage and inventory")
    plan = commands.add_parser("plan", help="Preview and write exact proposed settings; does not apply them")
    for p in (audit, plan):
        p.add_argument("--days", type=int, default=30)
        p.add_argument("--exclude-session", action="append", default=[])
    audit.add_argument("--html", type=Path, help="Write a new standalone offline report")
    audit.add_argument("--json", type=Path, help="Write a new local inventory with paths")
    plan.add_argument("--action", choices=("enable","disable"),required=True)
    select = plan.add_mutually_exclusive_group(required=True)
    select.add_argument("--pick", action="append", help="Repeat client:skill or codex:/absolute/path/SKILL.md")
    select.add_argument("--unused", action="store_true",help="Preview loaded skills with zero observed events")
    plan.add_argument("--include-partial",action="store_true",help="Include clients with partial evidence in an unused preview")
    plan.add_argument("--out", type=Path, required=True)
    apply = commands.add_parser("apply",help="Apply one reviewed local plan")
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--receipt",type=Path, required=True)
    recover = commands.add_parser("restore",help="Restore only the changes in an apply receipt")
    recover.add_argument("--receipt",type=Path,required=True)
    return root


def write_new(path,text):
    fd=os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        f.write(text)


def scan(args, clients):
    return {c:inventory(c,getattr(args,c+"_home"),args.cwd,not args.files_only,
                        agents_root=args.agents_root) for c in clients}


def analyze(args, clients, catalogs):
    if not 1 <= args.days <= 3660:
        raise ValueError("--days must be between 1 and 3660")
    now=datetime.now().astimezone()
    out={"days":args.days,"end":now.isoformat(timespec="seconds"),"clients":{}}
    for c in clients:
        excludes=set(args.exclude_session)
        active_vars=("CODEX_THREAD_ID",) if c=="codex" else ("CLAUDE_CODE_SESSION_ID","CLAUDE_SESSION_ID")
        excludes.update(os.environ[v] for v in active_vars if os.environ.get(v))
        cat=catalogs[c]
        by_path=collections.defaultdict(set)
        for entry in cat["items"]:
            if entry.get("path"):
                by_path[entry["path"]].add(entry["name"])
        path_names={path:next(iter(names)) for path,names in by_path.items() if len(names)==1}
        data=collect(args.claude_home,args.codex_home,args.days,now,exclude_ids=excludes,
                     clients=(c,),agents_root=args.agents_root,known_paths={c:path_names})[c]
        items=[];duplicates=collections.Counter(r["name"] for r in cat["items"])
        coverage=data["coverage"]
        for row in cat["items"]:
            name=row["name"];signals=data["skills"].get(name)
            exact=data["skill_paths"].get(row.get("path"))
            if duplicates[name]>1:
                metrics=exact
                if metrics is None and not signals and coverage["days_with_activity"]:
                    metrics=ZERO
            else:
                metrics=signals or exact or (ZERO if coverage["days_with_activity"] else None)
            aliases=[name]
            if name.startswith("anthropic-skills:"):
                aliases.append(name.partition(":")[2])
            hint_dates=[data.get(source,{}).get(alias) for source in ("ambiguous_native","ambiguous_invocation") for alias in aliases]
            ambiguous=max((date for date in hint_dates if date),default=None)
            if ambiguous and (not metrics or not metrics["events"]):
                metrics=None
            items.append(dict(row,metrics=metrics,duplicate=duplicates[name]>1,uncertain_last=ambiguous))
        items.sort(key=lambda r:(-(r["metrics"]["events"] if r["metrics"] else -1),r["name"],r["path"] or ""))
        out["clients"][c]={"live":cat["live"],"notes":cat["notes"],"coverage":coverage,"items":items}
    return out


def report_html(data):
    esc=lambda x:html.escape(str(x))
    blocks=[]
    for c,part in data["clients"].items():
        tables=collections.defaultdict(list)
        for r in part["items"]:
            m=r["metrics"]
            cells=[r["name"],TEXT[r["state"]],r["source"],m["events"] if m else "—",
                   m["sessions"] if m else "—",(m["last"] if m else r.get("uncertain_last")) or "—"]
            tables[r["state"]].append("<tr>"+"".join("<td>"+esc(x)+"</td>" for x in cells)+"</tr>")
        cv=part["coverage"]
        quality={"observed":"有活动记录","partial":"历史覆盖不完整","unavailable":"无可用历史"}[cv["status"]]
        probes="已读取实时技能目录" if part["live"] else "仅检查配置与磁盘"
        labels="".join("<th>"+t+"</th>" for t in ["Skill","状态","来源","使用证据数","涉及会话","最近使用"])
        notes=" ".join(part["notes"])
        if cv.get("blind_spots"):
            notes+=" 客户端可能不保留直接选用技能的证据。"
        contents=[]
        for state in ("loaded","candidate","disabled"):
            rows=tables[state]
            if not rows:
                continue
            grid=f"<div><table><thead><tr>{labels}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
            title=f"{TEXT[state]} · {len(rows)} 项"
            if state=="loaded" or (state=="candidate" and not part["live"]):
                contents.append(f"<h3>{title}</h3>{grid}")
            else:
                contents.append(f"<details><summary>{title}</summary>{grid}</details>")
        blocks.append(f"<section><h2>{NAME[c]}</h2><p>{probes} · {quality} · {cv['days_with_activity']} 个活跃日。{esc(notes)}</p>{''.join(contents)}</section>")
    style="body{font:15px/1.6 system-ui,sans-serif;color:#223b31;background:#f6f5ef;max-width:1040px;margin:auto;padding:24px}section{margin:28px 0}div{overflow-x:auto}table{background:white;border-collapse:collapse;width:100%}td,th{padding:8px;text-align:left;border-bottom:1px solid #d9e0d8}th{background:#e6eee6}td:first-child{overflow-wrap:anywhere}footer,p{color:#51645a}details{margin:1em 0}summary{cursor:pointer}td:nth-child(4),td:nth-child(5){font-variant-numeric:tabular-nums}"
    return ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>本机技能使用排行</title><style>"+style+"</style><main><h1>本机技能使用排行</h1><p>近 "+str(data["days"])+" 个自然日 · "+esc(data["end"])+"</p>"+"".join(blocks)+"<footer>按可归属的使用证据数排序。0 表示所读记录未检出，— 表示无可归属数据。账号同步、远程和项目级目录随客户端及工作目录而异。共享同名入口的按路径证据仅表示可归属的部分。</footer></main></html>")


def select_items(args, clients, catalogs):
    rows=[r for p in catalogs.values() for r in p["items"]]
    if args.unused:
        if args.action!="disable":
            raise ValueError("--unused is for disable plans")
        audited=analyze(args,clients,catalogs);targets=[]
        for c,p in audited["clients"].items():
            cv=p["coverage"]
            if not p["live"] or not cv["days_with_activity"] or ((cv["status"]!="observed" or cv.get("blind_spots")) and not args.include_partial):
                print(f"{c}: skipped bulk selection (live={p['live']}, coverage={cv['status']}, active days={cv['days_with_activity']}, incomplete signals={bool(cv.get('blind_spots'))}). --include-partial includes incomplete evidence in a preview.",file=sys.stderr)
                continue
            targets.extend(r for r in p["items"] if r["state"]=="loaded" and not r["duplicate"] and r["metrics"] and r["metrics"]["events"]==0)
        return targets
    targets=[]
    for ref in args.pick:
        client,sep,key=ref.partition(":")
        hits=[r for r in rows if r["client"]==client and (r["name"]==key or
              (client=="codex" and r["path"] and Path(key).is_absolute() and str(Path(key).resolve())==r["path"]))]
        if not sep or len(hits)!=1:
            raise ValueError(f"Unmatched or ambiguous selection: {ref}. Check client, scope and exact file.")
        if client=="claude" and sum(r["name"]==hits[0]["name"] and r['client']==client for r in rows)>1:
            raise ValueError("Claude name override would affect multiple entries")
        targets.append(hits[0])
    return targets


def main():
    args=parser().parse_args()
    ch=args.claude_home=args.claude_home.expanduser().resolve()
    xh=args.codex_home=args.codex_home.expanduser().resolve()
    args.cwd=args.cwd.expanduser().resolve()
    if not args.cwd.is_dir():
        raise ValueError("--cwd directory does not exist")
    clients=CLIENTS if args.client=="both" else (args.client,)
    if args.command=="restore":
        record=json.loads(args.receipt.read_text(encoding="utf-8"))
        if not set(record["plan"]["files"])<=set(clients):
            raise ValueError("Selected client scope does not include every client in this receipt")
        restore(args.receipt,ch,xh);print("本批设置已恢复。请在新会话复查。");return
    if args.command=="apply":
        plan=json.loads(args.plan.read_text(encoding="utf-8"))
        involved=set(plan["files"])
        if not involved or not involved<=set(clients):
            raise ValueError("Plan empty or chosen client scope does not cover it")
        clients=tuple(c for c in clients if c in involved)
    catalogs=scan(args,clients)
    rows=[r for p in catalogs.values() for r in p["items"] if r["client"]=="claude" or r.get("path")]
    if args.command=="apply":
        apply_plan(plan,ch,xh,rows,args.receipt)
        print("已写入配置。恢复凭据在",args.receipt,"。请以新进程 audit 核实加载状态。");return
    if args.command=="plan":
        targets=[dict(r,enabled=args.action=="enable") for r in select_items(args,clients,catalogs)]
        if not targets:
            print("没有符合条件的目标；没有生成计划。");return
        plan=make_plan(ch,xh,targets,rows)
        if not plan["changes"]:
            print("所选设置已是目标值。");return
        write_new(args.out,json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
        for change in plan["changes"]:
            print(change['client'],change['selector'],'=>',change['enabled'])
        print("仅预览，计划保存在",args.out);return
    data=analyze(args,clients,catalogs)
    if args.html:write_new(args.html,report_html(data))
    if args.json:write_new(args.json,json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    if not args.html and not args.json:
        print(json.dumps(data,ensure_ascii=False,indent=2))
    else:
        for c,p in data["clients"].items():
            print(NAME[c],len(p['items']),'entries;',p['coverage']['status'])

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,KeyError,TypeError,ControlError) as exc:
        print(f"Error: {exc}",file=sys.stderr);sys.exit(2)
