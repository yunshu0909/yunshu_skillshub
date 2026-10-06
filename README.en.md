<p align="right"><a href="./README.md">简体中文</a> · <strong>English</strong></p>

<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="Yunshu's Skills crew: a husky in a blue cap and two AI buddies walking across a floating island with seven little houses for coding, thinking, learning, writing, visualization, brand and agents" />
</p>

<h1 align="center">Yunshu SkillsHub</h1>

<p align="center"><strong>Methods I've collected from working with AI every day.</strong></p>

<p align="center">
  <a href="https://github.com/yunshu0909/yunshu_skillshub/stargazers"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/yunshu0909/yunshu_skillshub?style=flat-square&color=4E63D9" /></a>
  <a href="./LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-172033?style=flat-square" /></a>
  <img alt="25 skills" src="https://img.shields.io/badge/skills-25-E4AD53?style=flat-square&labelColor=172033" />
</p>

<p align="center">
  <a href="#coding">Coding</a> ·
  <a href="#thinking">Thinking</a> ·
  <a href="#learning">Learning</a> ·
  <a href="#writing">Writing</a> ·
  <a href="#visualization">Visualization</a> ·
  <a href="#brand">Brand</a> ·
  <a href="#agent">Agent</a>
</p>

## What this is

<img src="./assets/readme/scenes/about.jpg" width="100%" alt="Collected from real work: the husky finishes a job, writes down how it was done, and the AI buddies follow the handbook next time" />

These are the skills I've collected from working with AI every day.

Whenever I finish something, whether it's thinking a problem through, reading an article, writing a post or building a product, I write down how I asked, how I judged, and what "done" looked like, so next time the AI can follow the same path. None of these skills were designed in a vacuum. Each one has been used and revised on real work.

## Install

### Just ask your agent

Send this to Claude Code:

```text
Install the skills from https://github.com/yunshu0909/yunshu_skillshub into Claude Code at user level, so every project can use them. First list every skill with a one-line description and let me choose, then install the ones I pick, keeping each skill folder intact. When done, tell me what was installed and where.
```

Or send this to Codex:

```text
Install the skills from https://github.com/yunshu0909/yunshu_skillshub into Codex at user level, so every project can use them. First list every skill with a one-line description and let me choose, then install the ones I pick, keeping each skill folder intact. When done, tell me what was installed and where.
```

### With the CLI

```bash
# See what's available
npx skills add yunshu0909/yunshu_skillshub --list

# Pick a few, installed to both Claude Code and Codex
npx skills add yunshu0909/yunshu_skillshub -g -a claude-code codex --skill thinking-partner writing-assistant

# Install everything
npx skills add yunshu0909/yunshu_skillshub -g -a claude-code codex --skill '*' -y
```

### By hand

```bash
git clone https://github.com/yunshu0909/yunshu_skillshub.git

# One skill: copy the whole folder
cp -R yunshu_skillshub/thinking/thinking-partner ~/.claude/skills/   # Claude Code
cp -R yunshu_skillshub/thinking/thinking-partner ~/.agents/skills/   # Codex

# Everything (Claude Code shown; use ~/.agents/skills/ for Codex)
mkdir -p ~/.claude/skills
for f in yunshu_skillshub/*/*/SKILL.md; do cp -R "$(dirname "$f")" ~/.claude/skills/; done
```

After installing, just describe what you want to do, or name a skill. Keep each skill folder intact: the templates, references and scripts inside are part of the method. Most skills are written in Chinese.

<a id="coding"></a>

## Coding

<img src="./assets/readme/scenes/coding.jpg" width="100%" alt="Coding: the husky explains a flow board while one AI buddy codes and the other checks the work with a magnifier" />

Be clear about what you want before the AI starts building. From shaping requirements, designing and testing to changing code and shipping, every step can be checked.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Issue pool · `issue-pool`](./coding/issue-pool/SKILL.md) | Ideas, feedback and bugs need sorting out | `ISSUES.md` and problem statements ready to work on |
| [Page design · `page-solution-design`](./coding/page-solution-design/SKILL.md) | A page needs a full redesign or a fresh start | High-fidelity designs for every state, plus a handoff pack |
| [Backend logic · `backend-logic-design`](./coding/backend-logic-design/SKILL.md) | The rules are complex and need spelling out before coding | Rule tables and examples, with an interactive simulator if needed |
| [PRD & test cases · `prd-test-writer`](./coding/prd-test-writer/SKILL.md) | You want tests written alongside the requirements | A PRD and test cases that map one to one |
| [Dual-agent collaboration · `dual-agent-collaboration`](./coding/dual-agent-collaboration/SKILL.md) | An important change deserves a second AI's review | One agent builds, the other reviews read-only, until both sign off |
| [Requirement change · `req-change-workflow`](./coding/req-change-workflow/SKILL.md) | You need to change a feature that already exists | Impact analysis, a minimal change and a regression checklist |
| [Push & release · `git-push`](./coding/git-push/SKILL.md) | You're committing, pushing or cutting a release | Pre-push checks, the push, and the tag and Release |
| [Issue triage · `issue-triage`](./coding/issue-triage/SKILL.md) | Your open-source project got an issue | Root cause, a recommendation and a reply draft |
| [Repo search · `github-repo-search`](./coding/github-repo-search/SKILL.md) | You're looking for open-source projects to learn from | A compared shortlist |

> `dual-agent-collaboration` needs Codex and Claude Code installed locally; releases with `git-push` need `gh` logged in.

<a id="thinking"></a>

## Thinking

<img src="./assets/readme/scenes/thinking.jpg" width="100%" alt="Thinking: the husky and two AI buddies untangle a ball of yarn that leads to three glowing lanterns" />

Often you aren't stuck on doing, you're stuck on thinking. These help you untangle the problem, look from other angles, and make the call.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Thinking partner · `thinking-partner`](./thinking/thinking-partner/SKILL.md) | Things are messy and you can't say where you're stuck | A diagnosis, a few options and a next step |
| [Multi-perspective analysis · `multi-perspective-analysis`](./thinking/multi-perspective-analysis/SKILL.md) | You worry one line of thinking is boxing you in | Independent perspectives, with agreements, conflicts and blind spots |
| [Top three · `find-top-three`](./thinking/find-top-three/SKILL.md) | You need to choose a direction in life, career or business | The three things that matter most right now, and a step you can take today |

<a id="learning"></a>

## Learning

<img src="./assets/readme/scenes/learning.jpg" width="100%" alt="Learning: the husky reads at a lectern while the AI buddies make quiz cards and build a model" />

Between reading and understanding there's explaining it back, being tested, and putting it to use. Close-read a specific text, or map out an unfamiliar field first.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Close reading · `article-study`](./learning/article-study/SKILL.md) | You want to really understand an article, doc or codebase | Lesson pages, quizzes and a review of what you got wrong |
| [Systematic study · `system-study`](./learning/system-study/SKILL.md) | You want a structured view of a new field | A sourced knowledge map with cases and open debates |

<a id="writing"></a>

## Writing

<img src="./assets/readme/scenes/writing.jpg" width="100%" alt="Writing: scattered notes float toward a manuscript as the husky writes" />

Writing grows out of your own ideas. If your point is clear, build the outline and write. If it's still scattered, dig it out first.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Writing assistant · `writing-assistant`](./writing/writing-assistant/SKILL.md) | You want to go from topic to finished draft | A topic, an outline and a full first draft |
| [Thought mining · `thought-mining`](./writing/thought-mining/SKILL.md) | You have lots of fragments but no core point yet | The point you actually want to make, topic ideas and material |

<a id="visualization"></a>

## Visualization

<img src="./assets/readme/scenes/visualization.jpg" width="100%" alt="Visualization: a studio with a messy pile of paper on one side and a clear diagram on the easel" />

Make it easy to grasp at a glance: real examples of what others built, one clear idea per image, long reads people can follow to the end.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Case radar · `case-radar`](./visualization/case-radar/SKILL.md) | You want to see what people have actually built in a new space | A case gallery with screenshots and sources |
| [Image assistant · `image-assistant`](./visualization/image-assistant/SKILL.md) | An article or talk needs illustrations | What each image says, the exact on-image text, and prompts |
| [Readable output · `readable-output`](./visualization/readable-output/SKILL.md) | You want to turn notes, a retro or a tutorial into something people read | A well-structured HTML long read |

<a id="brand"></a>

## Brand

<img src="./assets/readme/scenes/brand.jpg" width="100%" alt="Brand: in a design workshop the husky picks among several emblem models" />

A name and a logo answer the same question: what is this product, who is it for, and what should people remember.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Product naming · `product-naming`](./brand/product-naming/SKILL.md) | You need a name for a product, project or module | Naming directions, candidates and the reasoning |
| [Logo design · `logo-design`](./brand/logo-design/SKILL.md) | You want to go from positioning to a usable logo and icon | Direction comparisons, refined drafts and app icons |

> `logo-design` needs Codex for image generation and editing.

<a id="agent"></a>

## Agent

<img src="./assets/readme/scenes/agent.jpg" width="100%" alt="Agent: the husky hands a scroll to an AI buddy about to set off, while the other files a card into a memory drawer" />

Handing work to an agent takes more than "go do it". It needs a clear goal and context it can remember.

| Skill | When to use it | What you get |
| --- | --- | --- |
| [Goal contract · `goal-setter`](./agent/goal-setter/SKILL.md) | You're handing a task to another agent to run on its own | A goal with scope, done criteria and stop conditions |
| [Project memory · `memory-init`](./agent/memory-init/SKILL.md) | A new project where you don't want to re-explain everything | `CLAUDE.md`, `MEMORY.md` and `memory/` |
| [Companion persona · `hermes-persona-builder`](./agent/hermes-persona-builder/SKILL.md) | You're defining a persona for Hermes or a companion agent | A ready-to-use `SOUL.md` |
| [Folder cleanup · `organize`](./agent/organize/SKILL.md) | Files have piled up and naming is a mess | A plan and a tidy folder |

## Say hi

If you'd like to get to know me or chat about working with AI, add me on WeChat.

<p align="center"><img src="./assets/readme/wechat-qr.jpg" width="220" alt="Yunshu's WeChat QR code" /></p>

Questions or ideas are also welcome as an [Issue](https://github.com/yunshu0909/yunshu_skillshub/issues). Version history is in the [CHANGELOG](./CHANGELOG.md).

---

<p align="center"><a href="./LICENSE">MIT License</a> · Made with care by Yunshu</p>
