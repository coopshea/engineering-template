# A shared brain for small engineering & product design teams

![](assets/header.png)

A Claude Code harness that turns the work you're already doing into a queryable record everyone on the team can use. As you work through a design problem with Claude, the conversation becomes structured documentation — design problem subdirectories, requirements with IDs, a risk register, a verified citation file. By the time someone else on the team needs context, it's already written down in a place they can find.

This is the scaffold I use for my own projects. I'm publishing it because the harness layer (the `CLAUDE.md` conventions, the source verification policy, the cross-reference tables) seems useful beyond my specific work, and small teams prototyping with coding agents like Claude Code might find it a reasonable baseline to fork or borrow from.

---

## What it actually does

Anyone on the team — including the non-engineers — can ask the agent things like:

- *"Why did we reject the cantilever needle approach?"*
- *"Show me every design decision that depends on the 20N actuation force assumption."*
- *"Pull the comparison matrix for the deflector geometry trade study and turn it into a slide."*
- *"Has anyone logged a risk related to suture pull-through?"*
- *"What sources do we have for the tissue mechanics numbers, and which are verified?"*

…and get real answers, with file paths, because the engineering work and the documentation are the same artifact. Decisions live in `engineering-log/[problem-name]/02_approach-survey.md`. Risks live in `risk-register.md` with stable RSK-IDs. Sources live in `sources.yaml` with a verification flag that the agent is not allowed to set on its own.

I used to think I needed RAG and embeddings and a variety of other hacks to do this, but now that most LLMs can be configured to have 1m+ context windows, I can just give them documents. Claude Code is a very capable harness for managing context and finding relevant info, and is even more so when organized in this manner.

The agent enforces the conventions on itself because they're written into `CLAUDE.md`, which Claude Code reads on every session.

Because the whole repo is in git, every change is timestamped and attributed automatically. That gives you a system of record for engineering decisions — when a requirement was added, when a risk was first logged, who proposed which approach, when a material was rejected and why — without anyone having to maintain that log by hand. In regulated industries (FDA Class II/III medical devices, FAA, IEC 62304 software, automotive ISO 26262), evidence of dated, attributed design decisions is a real submission requirement, not just hygiene. The branch-and-PR workflow in `AGENTS.md` is what turns "we have a git repo" into "we have a defensible design history." I'm sure this isn't good enough for formal submissions, but it is a much better on ramp for 0-1 concepting where a lot of this is lost in the ether and impossible to transmit.

## A worked example

Same setup throughout: two engineers and a clinical advisor prototyping an endoscopic suturing device, with needle deflection geometry as the active design problem.

### The individual experience — *document by doing*

Engineer A spends an afternoon evaluating three needle deflection geometries. Working with Claude, the conversation produces real artifacts as it happens. Constraints (tissue force, jaw envelope, bend radius) land in `requirements.md` as REQ-IDs. The three approaches end up in `02_approach-survey.md` with a comparison matrix and specific rejection reasons — buckling load, tissue compatibility, manufacturability. A tissue-mismatch failure mode goes into `risk-register.md` with an RSK linked back to the originating requirement.

By 6pm, the engineer hasn't written a single document *on top of* the work. The work itself is the document. Next week, the rejection reasons haven't compressed to "we tried that, it didn't work." Constraints haven't slipped. The risk hasn't been forgotten.

### The team experience — *shared context*

Wednesday, the clinical advisor scans the comparison matrix in two minutes and asks a sharp question. Engineer B picks up the problem next week, asks the agent *"what did A try and rule out, and why?"*, and gets a real answer with file paths. The Tuesday review surfaces an offhand *"we should revisit the cantilever with a thicker cross-section"* — the Notion sync drops the transcript into `meeting-notes/` and Claude routes the action item back into the needle-deflection README, linked to the transcript line.

Nobody is the bottleneck. The original engineer doesn't need to be in the room to re-explain yesterday's thinking. Advisor input doesn't get lost. Meeting remarks don't evaporate by Friday.

### The retrospective experience — *auditable history*

Three months later, a partnership conversation needs a slide deck. A patent attorney sits down for an hour. A regulatory consultant asks for the risk file. In each case the answer is "point at the files." The deck pulls from `02_approach-survey.md` and the comparison matrix. The attorney reads the rejected approaches as design-space coverage. The regulatory consultant reads `requirements.md` and `risk-register.md` and asks for cleanups, not a rebuild. Git holds the timestamps and attribution. Nobody had to "prepare" for any of these meetings.

---

This is roughly the system the people I most respect have always run by hand — tidy lab notebooks, every decision dated and sourced, the whole record assemblable on demand. I've never been able to sustain that kind of discipline; the documentation tax always felt bigger than the work. The bet here is that with Claude doing most of the capture in real time, the tax drops to near zero and the paper trail becomes a side effect of working.

## Who might find this useful

- **Small hardware or biomed teams (2–10 people)** where the same five people wear engineering, regulatory, IP, and clinical hats and need a shared source of truth that doesn't (yet) require a full PLM system. 
- **Student design teams** (capstone, thesis, competition robotics) who want a defensible written record of their reasoning alongside the working prototype.
- **Solo or small consultancies** doing technical design work where the deliverable includes "here's why we picked this."
- **Anyone using Claude Code as their primary engineering co-pilot** who has felt context get murky over time.

It is probably not useful for: pure software projects (different conventions apply), large orgs with an existing QMS, or anyone who wants a template they fill in once and never touch again.

## An honest note on source verification

The repo has a strict-ish source verification policy in `CLAUDE.md` and a `sources.yaml` file with verification tiers — Claude is not allowed to mark anything `verified: true` on its own. That stops the worst failure mode (the agent confidently citing a paper it never read), but it does not solve the LLM agreeableness problem: if you ask Claude to find sources that support a conclusion you've already reached, it will find them. So will Google Scholar. So will you. There is always *something* in the literature that supports any reasonable-sounding claim, and an agent biased toward being helpful will surface it.

The verification policy here is a weak patch job... it makes it too easy to trick yourself into having evidence, and Claude is quite happy skimming abstracts and pretending it has data it doesn't. I'd advise spending deliberate time navigating the literature *before* you've decided what you think. Use tools built for that — [OpenEvidence](https://openevidence.com) for clinical questions, [Litmaps](https://www.litmaps.com) or [Connected Papers](https://www.connectedpapers.com) for tracing citation networks, [Elicit](https://elicit.com) for structured literature review. These make that manual process much faster than doing random search by hand.

[Readwise](https://readwise.io) (or any equivalent) pairs well with this workflow: highlight as you read, sync the highlights into a personal corpus, and pipe that corpus into the engineering log when you're ready to cite. The advantage is that what you cite is what you actually read and digested — not what an agent fetched in response to a leading question. The verification flag in `sources.yaml` becomes meaningful instead of ceremonial.

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

In my own usage, a surprising amount of what determines a project's direction comes up in meetings as offhand remarks, half-finished thoughts, or "we should look into…" — items that aren't the top priority for the design team that week and kinda evaporate. Pulling the transcript into the repo automatically gives those moments a home. Six months later, when you're drafting an invention disclosure or a patent application, you can link from a leading concept doc back to the exact meeting where the idea first surfaced, with timestamp and attribution intact. That kind of provenance is hard to reconstruct after the fact and free if you capture it as you go. As an example, after a Tuesday review the script writes `meeting-notes/2026-04-28/summary.md` and `transcript.md`; Claude can then take the action item *"Engineer A: revisit the cantilever needle approach with thicker cross-section by next week"* and add it as a follow-up bullet in `engineering-log/needle-deflection/README.md`, with a link back to the meeting transcript line.

A user forking this repo will have to do their own setup work — creating a Notion integration, sharing their meetings database with it, and pasting their database ID into the script (steps in the docstring). The same pattern works for any note-taking system with an API: Granola, Otter, Fireflies, Read.ai, or whatever your team uses. Follow that tool's standard integration guide and adapt the script accordingly.

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
