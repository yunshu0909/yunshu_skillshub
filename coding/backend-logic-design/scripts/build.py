#!/usr/bin/env python3
"""从一份规则数据生成后端逻辑包：规则 md（冻结后追溯用）+ 可选的读者版 HTML。

rules.json 是编辑源（改规则只改它）；生成的规则 md 是冻结后给 PRD / 测试 / 审核追溯用的，不要手改。

用法：
  python3 build.py <数据目录> [--out <输出目录>] [--name <主题名>] [--draft]

  有 cards.json → 完整包：规则 md + 读者版 HTML
  没有 cards.json → 只出规则表：只生成规则 md
  还有 pending（待你定）或 proposed（材料里写了、你没拍过板）时必须加 --draft，产出标「草稿」

数据目录里放：
  rules.json  必需
    {
      "title": "审核配置",
      "rules": [
        { "id": 22,                        # 正整数，不重复，给用户看过就不重排
          "group": "⑤ 执行",                # 七块之一，见 GROUPS
          "rule": "一句规则",
          "case": "一个具体案例，用 → 串起来，最后一步是结果",
          "touch": ["A1", "T2"],            # 用户触点：前端状态编号（须在 frontStates 里）、T 编号（须在 touches 里）、
                                            #   ["无：<理由>"]，或回流期间的「候选：W16」（只允许 --draft）
          "status": "confirmed",            # 见 STATUS
          "source": "10-05 用户：……",        # confirmed / inherited 必填：原话或出处；proposed 必填：材料位置
          "confirmedText": "用户确认时的规则正文",  # confirmed 必填：确认那一刻的 rule 原文；之后 rule 改了字就要重新确认
          "constructed": false,             # 可省，布尔：案例是编的（页面标「构造」）
          "related": [21, 23],              # 可省：关联规则编号（审核复核「相邻边界」时看）
          "steps": [ { "step": "1 备份原件", "from": "冻结时的原件", "before": "…", "after": "…",
                       "verify": "…", "detect": "断在这一步怎么认出来", "recover": "怎么倒回去 / 接着做" } ],   # 可省：多步写操作
          "timeline": [ { "at": "0 秒", "what": "文件落盘" } ] }                                              # 可省：时间类规则
      ],
      "touches": { "T1": "验收页「审核」一栏" },      # 可省：无界面时的触点表（每个都要被至少一条规则用到）
      "frontStates": ["A1", "A2", "C1"],             # 可省：有界面时前端状态全集（用于触点校验和反向覆盖）
      "frontOnly": { "D2": "纯布局，无后端规则" },     # 可省：前端状态里没有后端规则的，写理由
      "notApplicable": { "⑦ 迁移": "新功能，没有旧东西" },   # 七块里没有规则的块必须写理由
      "devNotes": "markdown 文本"                    # 可省：技术细节，md 原样带上，HTML 里原样显示
    }
  cards.json  可省（完整包才要）
    {
      "ask": "第一句：要用户做什么", "lead": "一两句说明",
      "groups": [ { "id": "g1", "title": "…", "sub": "…", "sim": "sim-挑模型.html",
                    "cards": [ { "q": "问题？", "a": "一句答案。", "s": ["情景", "ok:结果", "stop:停下的结果"], "rules": [20, 25] } ] } ],
      "migration": { "sub": "一句说明", "rows": [ ["旧做法", "新做法", 39] ] }
    }
    小例子前缀：ok: 正常结果（绿）；stop: 停下 / 失败（红）；todo: 还没定（橙）；无前缀 = 普通情景。

输出：后端规则-<主题>.md（总有）、后端逻辑-<主题>.html（有 cards.json 时）。先全部在内存里生成，全部成功才写盘（先写临时文件再替换）。
"""
import argparse
import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUPS = ['① 数据和负责人', '② 加载', '③ 保存', '④ 默认值和升级', '⑤ 执行', '⑥ 出问题时', '⑦ 迁移']
STATUS = {'confirmed': '用户定', 'inherited': '已定·继承', 'proposed': '方案里有·你没拍板', 'pending': '待你定',
          'ai': 'AI 定', 'void': '作废'}
OPEN = ('pending', 'proposed')
REF = re.compile(r'后-(\d+)')
ASKING = re.compile(r'待你定|请你选|你来选|你来定|待用户定')
STEP_KEYS = ('step', 'from', 'before', 'after', 'verify', 'detect', 'recover')
RESERVED_IDS = {'cards', 'gm'}
ID_ATTR = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""")


class DataError(Exception):
    pass


def esc(text):
    return html.escape(str(text), quote=False)


def cell(text):
    """md 表格单元格：竖线、换行都转义，避免把表格拆坏。"""
    return str(text).replace('|', '／').replace('\r', ' ').replace('\n', ' ')


def rid(n):
    return f'后-{int(n):02d}'


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def nonempty(value):
    return isinstance(value, str) and value.strip() != ''


def load_json(path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise DataError(f'{path.name} 不是合法 JSON（第 {e.lineno} 行第 {e.colno} 列：{e.msg}）')


def validate(rules_doc, cards_doc, data_dir, draft):
    p = []
    if not isinstance(rules_doc, dict) or not isinstance(rules_doc.get('rules'), list) or not rules_doc['rules']:
        raise DataError('rules.json 里没有 rules 列表')
    touches = rules_doc.get('touches') or {}
    fronts = rules_doc.get('frontStates') or []
    front_only = rules_doc.get('frontOnly') or {}
    na = rules_doc.get('notApplicable') or {}
    if not isinstance(touches, dict) or not isinstance(fronts, list) or not isinstance(front_only, dict) or not isinstance(na, dict):
        raise DataError('touches / frontOnly / notApplicable 要是对象，frontStates 要是列表')
    if not all(isinstance(x, str) and x for x in fronts) or not all(isinstance(k, str) for k in list(touches) + list(front_only)):
        raise DataError('frontStates 里每一项、touches / frontOnly 的键都要是文字')
    if cards_doc is not None and not isinstance(cards_doc, dict):
        raise DataError('cards.json 最外层要是对象')
    by_id, used_touch = {}, set()
    for r in rules_doc['rules']:
        if not isinstance(r, dict):
            p.append(f'规则 {r!r}：要是对象')
            continue
        tag = f"规则 {r.get('id')!r}"
        if not is_int(r.get('id')):
            p.append(f'{tag}：id 必须是正整数')
            continue
        if r['id'] in by_id:
            p.append(f'{tag}：编号重复')
        by_id[r['id']] = r
        if r.get('group') not in GROUPS:
            p.append(f"{tag}：group「{r.get('group')}」不在七块里")
        for key in ('rule', 'case'):
            if not nonempty(r.get(key)):
                p.append(f'{tag}：{key} 为空或不是文字')
        if nonempty(r.get('case')) and '→' not in r['case']:
            p.append(f'{tag}：案例要用 → 串到结果')
        st = r.get('status')
        if not isinstance(st, str) or st not in STATUS:
            st = None
            p.append(f"{tag}：status 必须是 {' / '.join(STATUS)}")
        if st == 'confirmed':
            if not nonempty(r.get('confirmedText')):
                p.append(f'{tag}：用户定的规则要写 confirmedText（确认时的正文）')
            elif nonempty(r.get('rule')) and r['confirmedText'].strip() != r['rule'].strip():
                p.append(f'{tag}：正文和用户确认时不一样了，要重新确认（status 改回 pending）')
        if st in ('confirmed', 'inherited', 'proposed') and not nonempty(r.get('source')):
            p.append(f'{tag}：{STATUS.get(st)}的规则必须写 source（原话或出处）')
        if st not in OPEN and st != 'void' and nonempty(r.get('rule')) and ASKING.search(r['rule']):
            p.append(f'{tag}：正文写着要你定，但 status 是 {st}')
        if r.get('group') is not None and not isinstance(r.get('group'), str):
            p.append(f'{tag}：group 要是文字')
        if 'constructed' in r and not isinstance(r['constructed'], bool):
            p.append(f'{tag}：constructed 要是 true / false')
        touch = r.get('touch')
        if not isinstance(touch, list) or not touch or not all(nonempty(t) for t in touch):
            p.append(f'{tag}：touch 必须是非空文字列表')
            r['touch'] = [t for t in touch if nonempty(t)] if isinstance(touch, list) else []
        else:
            for t in touch:
                if t.startswith('候选'):
                    if not draft:
                        p.append(f'{tag}：「{t}」是回流中的候选状态，定稿前要换成签收后的状态编号')
                elif t.startswith('无'):
                    if not re.fullmatch(r'无[:：]\s*\S.*', t):
                        p.append(f'{tag}：「{t}」要写成「无：理由」')
                elif re.fullmatch(r'T\d+', t):
                    used_touch.add(t)
                    if t not in touches:
                        p.append(f'{tag}：触点 {t} 没在 touches 里说明')
                elif fronts and t not in fronts:
                    p.append(f'{tag}：前端状态 {t} 不在 frontStates 里')
                elif not fronts:
                    p.append(f'{tag}：触点「{t}」是前端状态编号，要先在 frontStates 里列出前端状态全集')
                else:
                    used_touch.add(t)
        for key in ('related',):
            if key in r and (not isinstance(r[key], list) or not all(is_int(x) for x in r[key])):
                p.append(f'{tag}：{key} 要是正整数列表')
        if 'steps' in r:
            if not isinstance(r['steps'], list) or not r['steps']:
                p.append(f'{tag}：steps 要是非空列表')
            else:
                for i, s in enumerate(r['steps'], 1):
                    miss = [k for k in STEP_KEYS if not isinstance(s, dict) or not nonempty(s.get(k))]
                    if miss:
                        p.append(f"{tag}：步骤表第 {i} 行缺 {'、'.join(miss)}")
        if 'timeline' in r:
            if not isinstance(r['timeline'], list) or not r['timeline'] or not all(isinstance(x, dict) and nonempty(x.get('at')) and nonempty(x.get('what')) for x in r['timeline']):
                p.append(f'{tag}：timeline 每一项要有 at 和 what')
    live = {i for i, r in by_id.items() if r.get('status') != 'void'}

    def refs(where, nums):
        for n in nums:
            if not is_int(n):
                p.append(f'{where}：编号 {n!r} 不是正整数')
            elif n not in by_id:
                p.append(f'{where}：引用了不存在的 {rid(n)}')
            elif n not in live:
                p.append(f'{where}：引用了已作废的 {rid(n)}')

    for r in by_id.values():
        if r.get('status') == 'void':
            continue
        text = str(r.get('rule', '')) + str(r.get('case', ''))
        refs(f"{rid(r['id'])} 正文/案例", [int(x) for x in REF.findall(text)])
        if isinstance(r.get('related'), list):
            refs(f"{rid(r['id'])} related", r['related'])
    refs('devNotes', [int(x) for x in REF.findall(str(rules_doc.get('devNotes', '')))])
    for k, v in front_only.items():
        if not nonempty(v):
            p.append(f'frontOnly 里 {k} 没写理由')
        elif k not in fronts:
            p.append(f'frontOnly 里 {k} 不在 frontStates 里')
    for t in touches:
        if t not in used_touch:
            p.append(f'触点 {t} 没有任何规则用到（删掉或补规则）')
    if fronts:
        covered = {t for r in by_id.values() if r.get('status') != 'void' for t in r.get('touch') or []}
        for s in fronts:
            if s not in covered and s not in front_only:
                p.append(f'前端状态 {s} 没有任何规则，也没在 frontOnly 里写理由')
    for g in GROUPS:
        has = any(r.get('group') == g and r.get('status') != 'void' for r in by_id.values())
        if not has and not nonempty(na.get(g)):
            p.append(f'七块里「{g}」没有规则，要在 notApplicable 里写理由')
    open_ = [rid(i) for i, r in by_id.items() if r.get('status') in OPEN]
    if open_ and not draft:
        p.append(f"还有待你定 / 你没拍过板的规则 {', '.join(open_)}：只能出草稿（加 --draft）")
    if cards_doc is not None:
        if not isinstance(cards_doc, dict) or not nonempty(cards_doc.get('ask')):
            p.append('cards.json：ask 为空')
        groups = cards_doc.get('groups') if isinstance(cards_doc, dict) else None
        if not isinstance(groups, list) or not groups:
            p.append('cards.json：没有 groups')
            groups = []
        gids, sim_ids = set(), {}
        all_gids = {g.get('id') for g in groups if isinstance(g, dict)}  # 先收齐所有分组 id，模拟器撞后面的分组也能拦住
        for g in groups:
            if not isinstance(g, dict) or not re.fullmatch(r'[A-Za-z][\w-]*', str(g.get('id', ''))) or g.get('id') in gids or g.get('id') in RESERVED_IDS:
                p.append(f"分组 id「{g.get('id') if isinstance(g, dict) else g}」非法、重复或和页面保留 id（{'、'.join(RESERVED_IDS)}）相撞")
                continue
            if not nonempty(g.get('title')):
                p.append(f"分组 {g['id']}：title 为空")
            gids.add(g['id'])
            if not g.get('cards'):
                p.append(f"分组「{g.get('title')}」没有卡片")
            if g.get('sim'):
                sp = (data_dir / str(g['sim'])).resolve()
                if data_dir.resolve() not in sp.parents or not sp.is_file():
                    p.append(f"分组「{g.get('title')}」的模拟器 {g['sim']} 要是数据目录里的文件")
                else:
                    for i in ID_ATTR.findall(sp.read_text()):
                        if i in sim_ids:
                            p.append(f'模拟器 {g["sim"]} 和 {sim_ids[i]} 用了同一个元素 id「{i}」')
                        elif i in RESERVED_IDS or i in all_gids:
                            p.append(f'模拟器 {g["sim"]} 的元素 id「{i}」和页面保留 id 或分组 id 相撞')
                        sim_ids.setdefault(i, g['sim'])
            for c in g.get('cards') or []:
                where = f"卡片「{c.get('q') if isinstance(c, dict) else c}」"
                if not isinstance(c, dict):
                    p.append(f'{where}：要是对象')
                    continue
                for key in ('q', 'a'):
                    if not nonempty(c.get(key)):
                        p.append(f'{where}：{key} 为空')
                if not isinstance(c.get('s'), list) or not c['s'] or not all(nonempty(x) for x in c['s']):
                    p.append(f'{where}：小例子 s 要是非空文字列表')
                if not isinstance(c.get('rules'), list) or not c['rules']:
                    p.append(f'{where}：没挂规则编号（rules），无法对账')
                else:
                    refs(where, c['rules'])
        mig = cards_doc.get('migration') if isinstance(cards_doc, dict) else None
        if mig is not None and (not isinstance(mig, dict) or not isinstance(mig.get('rows', []), list)):
            p.append('migration 要是 {sub, rows: [...]}')
            mig = None
        for row in (mig or {}).get('rows') or []:
            if not isinstance(row, list) or len(row) != 3:
                p.append(f'迁移行 {row}：要 [旧, 新, 规则编号]')
            else:
                refs(f'迁移「{row[0]}」', [row[2]])
    if p:
        raise DataError('数据有问题：\n- ' + '\n- '.join(p))
    return by_id


def step_html(t):
    for pre, cls in (('ok:', 'end'), ('stop:', 'badend'), ('todo:', 'todo'), ('!', 'end')):
        if t.startswith(pre):
            return f'<span class="{cls}">{esc(t[len(pre):].strip())}</span>'
    return f'<span>{esc(t)}</span>'


def card_html(c, by_id):
    st = {by_id[n].get('status') for n in c['rules']}
    if 'pending' in st:
        badge = '<span class="dec pend">待你定</span>'
    elif 'proposed' in st:
        badge = '<span class="dec pend">你没拍过板</span>'
    elif st & {'confirmed', 'inherited'}:
        badge = '<span class="dec">已定</span>'
    else:
        badge = ''
    made = any(by_id[n].get('constructed') for n in c['rules'])
    steps = '<i>→</i>'.join(step_html(s) for s in c['s'])
    ids = '、'.join(rid(n) for n in c['rules'])
    return (f'<div class="c{" pendc" if st & set(OPEN) else ""}"><p class="q">{esc(c["q"])}{badge}</p><p class="a">{esc(c["a"])}</p>'
            f'<div class="steps">{steps}</div><span class="id">{"例子是构造的 · " if made else ""}{ids}</span></div>')


def steps_md(r):
    out = ['', f"**{rid(r['id'])} 步骤表**", '', '| 步 | 来自哪一版 | 做之前 | 做之后 | 怎么验 | 断在这里怎么认出来 | 怎么倒回去 / 接着做 |', '|---|---|---|---|---|---|---|']
    for s in r['steps']:
        out.append('| ' + ' | '.join(cell(s.get(k, '')) for k in ('step', 'from', 'before', 'after', 'verify', 'detect', 'recover')) + ' |')
    return out


def timeline_md(r):
    return ['', f"**{rid(r['id'])} 时间轴**", ''] + [f"- {cell(x['at'])}：{cell(x['what'])}" for x in r['timeline']]


def render(rules_doc, cards_doc, by_id, name, draft, data_dir):
    rules = sorted(by_id.values(), key=lambda r: (GROUPS.index(r['group']), r['id']))
    touches = rules_doc.get('touches') or {}
    na = rules_doc.get('notApplicable') or {}
    tag = '（草稿：还有没拍板的规则）' if draft else ''
    md = [f'# 后端规则 · {name}{tag}', '',
          '> 编号 后-NN 是 PRD、测试用例和代码审核的追溯键。编辑源是 rules.json，本文件由它生成、不要手改。后端行为冲突以本文件为准；业务规则和已签收设计冲突时回到确认，不自动压过。', '']
    if touches:
        md += ['## 用户触点', '', '| 编号 | 触点 |', '|---|---|'] + [f'| {cell(k)} | {cell(v)} |' for k, v in touches.items()] + ['']
    fronts = rules_doc.get('frontStates') or []
    if fronts:
        front_only = rules_doc.get('frontOnly') or {}
        md += ['## 前端状态 ↔ 规则', '', '| 前端状态 | 规则 | 纯前端的理由 |', '|---|---|---|']
        for f in fronts:
            hits = '、'.join(rid(r['id']) for r in rules if f in (r.get('touch') or []))
            md.append(f'| {cell(f)} | {hits} | {cell(front_only.get(f, ""))} |')
        md.append('')
    extras = []
    for grp in GROUPS:
        rows = [r for r in rules if r['group'] == grp]
        if not rows:
            md += [f'## {grp}', '', f'不适用：{na.get(grp, "")}', '']
            continue
        md += [f'## {grp}', '', '| # | 规则 | 用户触点 | 案例 | 状态 | 出处 | 关联 |', '|---|---|---|---|---|---|---|']
        for r in rows:
            case = ('（构造）' if r.get('constructed') else '') + r['case']
            rel = '、'.join(rid(x) for x in r.get('related') or [])
            md.append(f"| {rid(r['id'])} | " + ' | '.join(cell(c) for c in [r['rule'], '、'.join(r['touch']), case, STATUS[r['status']], r.get('source', ''), rel]) + ' |')
            if r.get('steps'):
                extras += steps_md(r)
            if r.get('timeline'):
                extras += timeline_md(r)
        md.append('')
    if extras:
        md += ['## 步骤表与时间轴'] + extras + ['']
    if cards_doc:
        md += ['## 卡片对账（封装前逐行核：卡片说法不许比所挂规则说得更满）', '', '| 卡片 | 一句答案 | 规则 |', '|---|---|---|']
        for g in cards_doc['groups']:
            for c in g['cards']:
                md.append(f"| {cell(c['q'])} | {cell(c['a'])} | {'、'.join(rid(n) for n in c['rules'])} |")
        md.append('')
    if rules_doc.get('devNotes'):
        md += ['## 技术细节', '', str(rules_doc['devNotes']).strip(), '']
    outputs = {f'后端规则-{name}.md': '\n'.join(md)}
    if not cards_doc:
        return outputs, len(rules), 0
    template = (HERE.parent / 'assets' / 'template.html').read_text()
    sections, toc = [], ''
    for g in cards_doc['groups']:
        sim = (data_dir / g['sim']).read_text() if g.get('sim') else ''
        body = sim + ''.join(card_html(c, by_id) for c in g['cards'])
        sections.append(f'<section class="grp" id="{g["id"]}"><h2>{esc(g["title"])}</h2><p>{esc(g.get("sub", ""))}</p>{body}</section>')
        toc += f'<a href="#{g["id"]}">{esc(g["title"])}</a>'
    mig = cards_doc.get('migration') or {}
    if mig.get('rows'):
        rows = ''.join(f'<div class="r"><span class="old">{esc(o)}</span><span class="ar">→</span><span class="new">{esc(n)} <span class="mid">{rid(i)}</span></span></div>' for o, n, i in mig['rows'])
        sections.append(f'<section class="grp" id="gm"><h2>现在的东西会变成什么样</h2><p>{esc(mig.get("sub", ""))}</p><div class="mig">{rows}</div></section>')
        toc += '<a href="#gm">现在的东西会变成什么样</a>'
    appendix = []
    for grp in GROUPS:
        rows = [r for r in rules if r['group'] == grp]
        if not rows:
            continue
        trs = ''.join(f'<tr class="st-{r["status"]}"><td>{rid(r["id"])}</td><td>{esc(r["rule"])}</td><td>{esc("、".join(r["touch"]))}</td>'
                      f'<td>{"（构造）" if r.get("constructed") else ""}{esc(r["case"])}</td><td>{STATUS[r["status"]]}</td></tr>' for r in rows)
        appendix.append(f'<h4>{esc(grp)}</h4><div class="tw"><table><tr><th>#</th><th>规则</th><th>触点</th><th>案例</th><th>状态</th></tr>{trs}</table></div>')
    if extras:
        appendix.append(f'<h4>步骤表与时间轴</h4><pre class="notes">{esc(chr(10).join(extras))}</pre>')
    if rules_doc.get('devNotes'):
        appendix.append(f'<h4>技术细节</h4><pre class="notes">{esc(rules_doc["devNotes"])}</pre>')
    n_cards = sum(len(g['cards']) for g in cards_doc['groups'])
    n_open = sum(1 for r in rules if r['status'] in OPEN)
    lead = esc(cards_doc.get('lead', '')) + f'（{n_cards} 张卡；完整规则 {len(rules)} 条在最底下的折叠里' + (f'；<b class="pendt">{n_open} 条要你看</b>' if n_open else '') + '）'
    page = (template.replace('__TITLE__', esc(name) + esc(tag)).replace('__ASK__', esc(cards_doc['ask']))
            .replace('__LEAD__', lead).replace('__TOC__', toc).replace('__CARDS__', ''.join(sections))
            .replace('__NRULES__', str(len(rules))).replace('__APPENDIX__', ''.join(appendix)))
    outputs[f'后端逻辑-{name}.html'] = page
    return outputs, len(rules), n_cards


def write_all(out, outputs):
    """先把所有新文件写成临时文件；再把旧文件改名成备份、新文件改名到位（全程只改名、不回写内容）。
    任何一步失败：把已到位的新文件移走、备份改名回原名，不留新旧混在一起的产物，也不会因回写失败截空旧文件。"""
    out.mkdir(parents=True, exist_ok=True)
    tmps, moved = [], []
    try:
        for fname, text in outputs.items():
            fd, tmp = tempfile.mkstemp(dir=out, prefix='.tmp-', suffix='-' + fname)
            with os.fdopen(fd, 'w') as f:
                f.write(text)
            tmps.append((tmp, out / fname))
        for tmp, dest in tmps:
            bak = None
            if dest.exists() or dest.is_symlink():
                bak = str(dest) + '.bak-build'
                os.replace(dest, bak)
            moved.append((dest, bak))
            os.replace(tmp, dest)
    except OSError:
        for dest, bak in reversed(moved):
            try:
                if dest.exists() and not dest.is_dir():
                    dest.unlink()
                if bak:
                    os.replace(bak, dest)
            except OSError:
                print(f'回退失败：旧版留在 {bak}，请手动改回 {dest.name}', file=sys.stderr)
        raise
    else:
        for _, bak in moved:
            if bak and os.path.exists(bak):
                os.unlink(bak)
    finally:
        for tmp, _ in tmps:
            if os.path.exists(tmp):
                os.unlink(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('--out')
    ap.add_argument('--name')
    ap.add_argument('--draft', action='store_true')
    a = ap.parse_args()
    data = Path(a.data)
    out = Path(a.out) if a.out else data
    try:
        rules_doc = load_json(data / 'rules.json')
        cards_path = data / 'cards.json'
        cards_doc = load_json(cards_path) if cards_path.exists() else None
        if cards_path.exists() and cards_doc is None:
            raise DataError('cards.json 是空值（null）：不要卡片就删掉这个文件')
        by_id = validate(rules_doc, cards_doc, data, a.draft)
        name = a.name or rules_doc.get('title', '主题')
        if not isinstance(name, str) or not re.fullmatch(r'[\w一-鿿·-]+', name):
            raise DataError(f'主题名「{name}」不能做文件名')
        outputs, n_rules, n_cards = render(rules_doc, cards_doc, by_id, name, a.draft, data)
        write_all(out, outputs)
    except (DataError, OSError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except (TypeError, KeyError, AttributeError, ValueError) as e:
        print(f'数据结构不对（{type(e).__name__}：{e}），请对照 build.py 开头的格式说明', file=sys.stderr)
        sys.exit(1)
    n_open = sum(1 for r in by_id.values() if r.get('status') in OPEN)
    mode = '只出规则表' if cards_doc is None else f'{n_cards} 张卡'
    print(f'ok：{n_rules} 条规则、{mode}{"、" + str(n_open) + " 条待你看（草稿）" if n_open else ""} → {out}')
    print('提醒：构建通过只说明结构完整，不代表语义对、边界全；卡片对账、边界审查仍要人和另一家模型做。')


if __name__ == '__main__':
    main()
