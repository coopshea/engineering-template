# Engineering Documentation Template

A Claude Code harness for engineering projects. The idea: while you're working through a design problem with Claude, the conversation becomes structured documentation — design problem subdirectories, requirements with IDs, a risk register, a verified citation file. By the time someone else on the team needs context, it's already written down in a place they can find.

This is the scaffold I use for my own projects. I'm publishing it because the harness layer (the `CLAUDE.md` conventions, the source verification policy, the cross-reference tables) seems useful beyond my specific work, and small teams prototyping with coding agents like Claude Code might find it a reasonable baseline to fork or steal from.

---

## What it actually does

Anyone on the team — including the non-engineers — can ask the agent things like:

- *"Why did we reject the cantilever needle approach?"*
- *"Show me every design decision that depends on the 20N actuation force assumption."*
- *"Pull the comparison matrix for the deflector geometry trade study and turn it into a slide."*
- *"Has anyone logged a risk related to suture pull-through?"*
- *"What sources do we have for the tissue mechanics numbers, and which are verified?"*

…and get real answers, with file paths, because the engineering work and the documentation are the same artifact. Decisions live in `engineering-log/[problem-name]/02_approach-survey.md`. Risks live in `risk-register.md` with stable RSK-IDs. Sources live in `sources.yaml` with a verification flag that the agent is not allowed to set on its own.

The agent enforces the conventions on itself because they're written into `CLAUDE.md`, which Claude Code reads on every session.

## A worked example

Two engineers and a clinical advisor are prototyping an endoscopic suturing device. On Tuesday, Engineer A spends the afternoon evaluating three needle deflection geometries. Working with Claude, they end up with `engineering-log/needle-deflection/` containing a problem definition, a comparison matrix of the three approaches with specific rejection reasons (force budget, buckling load, tissue compatibility), and a leading concept doc. Two new requirements get added to `requirements.md` and a tissue-mismatch hazard gets logged in `risk-register.md`.

Wednesday morning, the clinical advisor reads the comparison matrix in two minutes and asks a sharp question about one of the rejected approaches. The conversation moves quickly because the trade-off is already in front of both of them.

A month later, a patent attorney sits down for an hour. The engineer points at the same comparison matrix and at `engineering-log/competitive-reference/patents/README.md`. The attorney leaves with what they need. Nobody had to "prepare for the patent meeting."

The point isn't that this couldn't happen with regular notes. It's that the engineer was already doing the thinking — the harness just captured it in a shape that's useful to the advisor, the attorney, and the next engineer to touch the file.

## Who might find this useful

- **Small hardware or biomed teams (2–10 people)** where the same five people wear engineering, regulatory, IP, and clinical hats and need a shared source of truth that doesn't require a full PLM system.
- **Student design teams** (capstone, thesis, competition robotics) who want a defensible written record of their reasoning alongside the working prototype.
- **Solo or small consultancies** doing technical design work where the deliverable to the client includes "here's why we picked this."
- **Anyone using Claude Code as their primary engineering co-pilot** who has felt context vanish between sessions and wants the agent to write things down in a structured place by default.

It is probably not useful for: pure software projects (different conventions apply), large orgs with an existing QMS, or anyone who wants a template they fill in once and never touch again.

## What's in the repo

- `CLAUDE.md` — the agent instructions. Format standards, source verification policy, design problem subdirectory conventions, team collaboration rules. This is the most transferable file in the repo.
- `AGENTS.md` — git workflow + onboarding for human and AI contributors.
- `engineering-log/` — the working area. Cross-reference tables (`requirements.md`, `risk-register.md`, `material-selections.md`, `sources.yaml`), a master `INDEX.md`, and a place for design problem subdirectories.
- `scripts/fetch_notion_meetings.py` — a script that pulls meeting notes from Notion into `meeting-notes/YYYY-MM-DD/`. Bring your own integration token and database ID; setup steps are in the script docstring. A reference `SKILL_meeting-notes.md` is included for installing it as a `/meeting-notes` Claude Code skill.
- Standard project folders: `ip-drafts/`, `meeting-notes/`, `governance/`, `financials/`, `invoices/`.

The cross-reference tables ship empty. There's no project content here — just the scaffolding.

## Optional: Obsidian, Notion meetings, and other skills

Because the whole repo is just markdown files, you can open it in [Obsidian](https://obsidian.md) and get a graph view, backlinks between design problems, and inline previews of figures. Useful when you want to *look* at the project rather than query it through the agent — especially handy for showing teammates how things connect. The repo's `.gitignore` ignores Obsidian's `.obsidian/` workspace folder so each user can configure their own view.

The included Notion meeting-notes skill is intended for the team meeting workflow: someone runs `/meeting-notes` after a meeting, the script pulls the transcript and action items from Notion, and Claude can then route them — turning action items into roadmap entries, risk register rows, follow-up tasks in the relevant design problem subdirectory, or notes flagged for the next agenda. The same content shows up in Obsidian's graph view as a meeting node connected to whichever design problems it touched.

Add other skills as your team's tooling demands. A Linear sync (for teams that want a stronger external task manager than Notion), a Slack digest pull, a GitHub issue importer — same pattern: a script does the API call and writes to disk, a SKILL.md teaches Claude how to invoke it conversationally. The `Custom Skills & Integrations` section of `CLAUDE.md` covers the convention.

## Quick start

```bash
# Use as a GitHub template (button at top of the repo page) or clone directly
git clone https://github.com/coopshea/engineering-template my-project
cd my-project

# Replace [PROJECT NAME] and [YOUR NAME] across the repo
# In CLAUDE.md, fill in Project Overview, Primary User Scope, and the Team Collaboration table

# Open in Claude Code — it reads CLAUDE.md automatically
```

## Steal the pattern

The most useful artifact here is `CLAUDE.md`. If you don't want the whole template, lift that file into your existing repo and adapt it. The conventions worth copying:

1. Cross-reference tables (requirements, risks, materials, sources) maintained as markdown files the agent updates incrementally each session.
2. Design problem subdirectories with a comparison matrix in the approach survey — this single file is what later becomes a patent claim or a regulatory rationale.
3. A source verification policy where the agent cannot mark anything `verified: true` on its own.
4. Authoritative-vs-working-notes distinction so the agent knows which files to cite and which to treat as working state.
5. Skills that wrap external integrations (Notion, Linear, etc.) so heavy content syncs to disk without burning tokens.

Issues and PRs welcome if you adopt this and find a convention worth adding to the harness layer.

## License

MIT.
