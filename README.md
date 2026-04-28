# Engineering Documentation Template

**A Claude Code harness for engineering projects: as you do the work, the documentation builds itself.**

This is a template repo. Clone it as the starting point for an engineering project — hardware, mechanical design, regulated devices, IP-heavy R&D — where you want a paper trail that can later become a Design History File, a regulatory submission, a patent filing, or just a deck for your investors. Without writing it twice.

The template is the **agent harness layer**: a directory structure, a set of Claude Code instructions (`CLAUDE.md`), a few skills, and conventions that teach Claude to treat this repo as the project's source of truth. There's no project content in here — only the scaffolding.

---

## Why this exists

Small engineering teams have the same problem at every stage:

- The CAD lives in someone's head and on a hard drive.
- The "why we picked this material" lives in a Slack thread from three weeks ago.
- The risk you flagged in a meeting got captured as "we should think about that more later."
- When the regulatory consultant, the patent attorney, the investor, or the new hire shows up, you spend a week reconstructing what the team already knew.

The standard answer is "be more disciplined about documentation." That doesn't work, because the engineer who just figured out a tricky design decision wants to keep designing — not stop and write a paragraph for someone who isn't in the room.

This template is the other answer: **co-author the documentation with Claude as you go.** The conventions are tight enough that the output is consistent across sessions, contributors, and agents — and structured enough that it converts cleanly into the artifacts non-technical teammates actually need (slides, summaries, regulatory inputs, patent filings).

---

## A contrived example

You're a small team prototyping a new endoscopic suturing device. Two engineers, a clinical lead, and a part-time advisor. You meet on Tuesdays.

**Tuesday morning, before the meeting.** Engineer A spent yesterday afternoon evaluating three different needle deflection geometries. The math says one wins, but only in certain tissue conditions. They open Claude Code and say:

> "I'm working on the needle deflection problem. I tried three approaches: a straight cantilever, a curved fixed deflector, and a sigmoid two-stage deflector. Help me document this."

Claude reads `CLAUDE.md`, sees the design-problem subdirectory convention, and creates `engineering-log/needle-deflection/` with a `README.md`, `01_problem-definition.md`, and a `02_approach-survey.md` containing a comparison matrix. It asks the engineer for the rejection reasons (force budget? buckling? tissue compatibility?), captures them with specific numbers, and updates `requirements.md` with two new REQ-IDs and `risk-register.md` with a tissue-mismatch hazard. Total time: 20 minutes that the engineer would have spent thinking anyway.

**Tuesday afternoon, the meeting.** The clinical lead asks "wait, didn't we rule out the cantilever last month?" The engineer pulls up `engineering-log/needle-deflection/02_approach-survey.md`, scrolls to the comparison matrix, and points at the cell that says "rejected — buckling load 3.7N below required actuation force 5N." The conversation moves on in 30 seconds instead of 30 minutes.

**Wednesday.** The advisor wants a one-pager for a potential partnership conversation. The engineer says to Claude:

> "Make me a one-page summary of where we are on needle deflection, written for a non-engineer. Include the leading concept and the two open questions."

Claude reads `04_leading-concept.md`, the open questions section, and the linked risk register entries. It produces a clean summary in plain language that the engineer reviews and edits in five minutes. The advisor gets it that afternoon.

**Two weeks later.** A patent attorney joins for an hour. The engineer points them at `engineering-log/needle-deflection/02_approach-survey.md` for the design-space coverage and `engineering-log/competitive-reference/patents/README.md` for the prior art the team has surfaced so far. The attorney leaves with everything they need to draft a provisional. No one had to "prepare for the patent meeting."

**A month later.** A regulatory consultant asks for the risk file and requirements traceability. The engineer hands them `risk-register.md` and `requirements.md`. The consultant says "this is already 80% of an ISO 14971 input." The team didn't know what ISO 14971 was when they started.

**The point:** none of this required the engineers to stop engineering. They were going to think about the rejection reasons anyway. They were going to talk through the trade-offs anyway. The template just captures it in a shape that's useful to everyone else, automatically.

---

## What you get

1. **A documentation system designed for AI co-authorship.** `CLAUDE.md` tells Claude how to write engineering log entries, where to put them, when to update cross-reference tables, and what to do when it can't verify a citation.

2. **A source verification policy that doesn't lie.** Claude can confidently hallucinate a citation. This template makes that hard: every reference goes into `sources.yaml` with a verification tier, and only the human user marks something `verified: true`. Claude can locate, summarize, and queue sources — it cannot vouch for them.

3. **Cross-reference tables that turn into a regulatory file.** `requirements.md` (REQ-IDs), `risk-register.md` (RSK-IDs), `material-selections.md`, and `sources.yaml` get updated incrementally during every session. Formalization later is assembly, not archaeology.

4. **Design problem subdirectories that double as patent prep.** Each design problem gets a problem definition, an approach survey with comparison matrix, calculations, and a leading concept. The approach survey is the highest-value document: it serves engineering decision-making AND patent claim coverage simultaneously.

5. **A meeting-notes skill out of the box.** `scripts/fetch_notion_meetings.py` pulls meeting notes from Notion and writes them to `meeting-notes/YYYY-MM-DD/` with zero LLM tokens used for the bulk content. Bring your own Notion integration (~5 minute setup). A reference SKILL.md is provided to install it as `/meeting-notes`.

6. **Team workflow conventions.** `AGENTS.md` documents the branch-and-PR workflow, who works in which directories, and the rules every contributor (human or agent) follows.

## Who this is for

- **Small hardware/biomed teams (2–10 people)** prototyping toward a real product, where the IP and the regulatory paper trail will both matter eventually.
- **Solo or small-team consultancies** doing technical design work that needs to be defensible to clients later.
- **University labs or thesis projects** where the deliverable is both a working prototype and a written record of why it works.
- **Anyone using Claude Code as their primary engineering co-pilot** who has felt the pain of context vanishing between sessions.

It is *not* a fit for: pure software projects (different conventions apply), large org-wide PLM/QMS replacements (this is a scaffold, not a system), or anyone who wants their LLM to confidently cite papers it hasn't read (we explicitly prevent that).

## What this template is NOT

- Not a project. No IP, no product, no real data. Cross-reference tables empty. Fill them in as you go.
- Not a quality management system. It's the early-stage scaffold that becomes the inputs to a QMS, DHF, or patent filing when the time comes.
- Not opinionated about your domain. Mechanical, biomedical, electrical, materials — the conventions apply anywhere "what we tried, why we picked this, here's the math, here's the source" is the right output shape.

---

## Quick Start

```bash
# 1. Use as a GitHub template, or clone and reset history
git clone <this-repo-url> my-project
cd my-project

# 2. Replace placeholders
#    - [PROJECT NAME] → your project name
#    - [YOUR NAME]    → your name
#    - In CLAUDE.md, fill in Project Overview, Primary User Scope, Team Collaboration table

# 3. (Optional) Set up Notion meeting-notes sync
#    See scripts/fetch_notion_meetings.py docstring for setup steps

# 4. Open in Claude Code and start working
#    Claude reads CLAUDE.md automatically and follows the conventions
```

| What you need | Where to find it |
|---------------|-----------------|
| AI agent instructions | `CLAUDE.md` |
| Git workflow + onboarding | `AGENTS.md` |
| Master index of design problems | `engineering-log/INDEX.md` |
| Requirements (REQ-IDs) | `engineering-log/requirements.md` |
| Risk register | `engineering-log/risk-register.md` |
| Material selections | `engineering-log/material-selections.md` |
| Sources + verification status | `engineering-log/sources.yaml` |
| Notion meeting-notes script | `scripts/fetch_notion_meetings.py` |

## Directory Structure

```
├── CLAUDE.md                    ← AI agent instructions
├── AGENTS.md                    ← Git workflow + team onboarding
├── README.md                    ← this file
├── .gitignore
├── engineering-log/             ← Design problems + cross-reference tables
│   ├── INDEX.md                 ← start here
│   ├── requirements.md
│   ├── risk-register.md
│   ├── material-selections.md
│   ├── sources.yaml / .md
│   ├── hours-log.csv
│   ├── [problem-name]/          ← one folder per design problem
│   └── competitive-reference/   ← public-domain prior art
├── ip-drafts/                   ← Patent drafts, invention disclosures
├── meeting-notes/               ← Auto-imported from Notion (optional)
├── governance/                  ← IP / collaboration agreements
├── financials/ + invoices/      ← Expense tracking
└── scripts/                     ← Integration scripts (Notion sync, etc.)
```

## Patterns Worth Knowing

### Hand calculations as Jupyter notebooks

For calc-heavy design problems (force budgets, stress analysis, sizing studies), Jupyter notebooks (`03_calculations.ipynb`) work better than markdown: equations render, results update when constants change, and the notebook is a runnable artifact. The template doesn't ship example notebooks (those are project-specific), but the pattern is:

- Define shared constants in a single `constants.py` at the engineering-log root
- Each notebook imports from there — single source of truth
- Notebooks live in the design problem subdirectory alongside the markdown docs
- Archive any markdown that gets migrated as `.md.archived` rather than deleting it

### Authoritative vs. working notes

Not everything is equally trustworthy:

- **Authoritative** — leading concept docs, cross-reference tables, sources marked `verified: true` or `verified: user`
- **Working notes** — approach surveys, calculations, problem definitions, standalone dated entries, anything `verified: false`

Claude treats these differently when citing or building on them.

### Skills, not scripts

If you find yourself running an integration regularly (Notion sync, Linear ticket fetch, Slack digest export), wrap it in a Claude Code skill so you can invoke it conversationally. The script does the API call and writes to disk; Claude reads the disk afterward — minimal token usage, maximum reuse. See "Custom Skills & Integrations" in `CLAUDE.md`.

### Generating slides and summaries from the log

Once the engineering log has structure, generating downstream artifacts is mostly a matter of pointing Claude at the right files:

- **Investor / partner one-pager:** "Summarize the leading concepts across all design problems for a non-engineer. One paragraph each, plus open questions."
- **Slide deck:** "Make a 10-slide deck on the current state of [subsystem]. Use the comparison matrix from `02_approach-survey.md` for the trade-study slide. Pull figures from each `assets/` folder."
- **Regulatory input:** "Cross-reference the risk register against requirements.md and flag any RSK without a linked REQ."
- **Patent prep:** "List every approach in `02_approach-survey.md` files repo-wide that was rejected for a reason other than 'didn't seem feasible.' Group by design problem."

The structure exists so that the slide deck doesn't require re-explaining the project to Claude every time.

---

## Contributing

If you're using this template and find a convention that should be in the harness layer (not your project), open a PR upstream. Things that belong here: agent instructions, format standards, skill scaffolding, workflow conventions. Things that don't: your project's IP, requirements, citations, or design content.

## License

MIT for the template scaffold itself. Whatever you decide for content you add to your fork.
