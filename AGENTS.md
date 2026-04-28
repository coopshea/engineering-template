# AGENTS.md — Git Workflow & Team Onboarding

This file helps team members (and their AI agents) contribute to this repo. For format standards, source verification policy, and engineering conventions, see `CLAUDE.md` — everything there applies to all contributors.

**Who works where** is defined in `CLAUDE.md` (Team Collaboration section). Don't duplicate it here — check there for the authoritative role-to-directory mapping.

---

## Git Workflow (Step by Step)

This repo uses a branch-and-PR workflow. **Never commit directly to `master`.** All changes go through a pull request reviewed by the primary user.

### First Time Setup

```bash
# Clone the repo (only needed once)
git clone <repo-url>
cd <repo-name>

# Confirm you're on master and up to date
git checkout master
git pull origin master
```

### Every Work Session

**1. Start fresh from master**

```bash
git checkout master
git pull origin master
```

**2. Create a branch for your work**

Name it `[your-name]/[short-description]`. Lowercase, hyphens.

```bash
git checkout -b yourname/short-description
```

**3. Do your work** — create/edit files following the format standards in `CLAUDE.md`.

**4. Stage and commit your changes**

Stage specific files (don't use `git add .` or `git add -A`):

```bash
git add path/to/file.md
git commit -m "Short description of what changed and why"
```

**5. Push your branch**

```bash
git push -u origin yourname/short-description
```

**6. Open a pull request**

```bash
gh pr create --title "Short title" --body "What changed and why."
```

Or open it via the GitHub web UI.

**7. Wait for review** — the primary user will review and merge. If changes are requested, make them on the same branch and push again.

### Common Situations

**"I already have a branch and want to add more changes"**

```bash
git checkout yourname/short-description
# make changes
git add [files]
git commit -m "Description of additional changes"
git push
```

**"My branch is behind master"**

```bash
git checkout yourname/short-description
git pull origin master
# resolve any conflicts if prompted
git push
```

**"I made changes on master by accident"**

Don't panic. Move them to a new branch before committing:

```bash
git stash
git checkout -b yourname/accidental-changes
git stash pop
git add [files]
git commit -m "Description"
git push -u origin yourname/accidental-changes
```

**"I'm not sure what state things are in"**

```bash
git status            # changed/staged files
git branch            # current branch (* = current)
git log --oneline -5  # recent commits
```

---

## Competitive Reference — Structure for Patent & Prior Art Work

If your project tracks competitor devices or patent prior art, use this structure under `engineering-log/competitive-reference/`. All sources must be freely available (USPTO, Google Patents, FDA 510(k) database, manufacturer publications). **No confidential or licensed material here.**

```
engineering-log/competitive-reference/
├── README.md              ← Index and context
├── devices/               ← Competitor product specs and dimensions
│   └── [product-name].md
├── patents/               ← Published patent references
│   ├── README.md          ← Patent index table (bulk entry point)
│   └── [patent-number]_short-name.md  ← Detailed notes (only for key patents)
└── assets/                ← Images from patents, device photos
```

**For bulk patent entry**, most patents only need a row in `patents/README.md`:

```markdown
| Patent # | Assignee | Title | Relevance | Link |
|----------|----------|-------|-----------|------|
| US10,XXX,XXX | [Company] | [Title] | [why it matters] | [Google Patents link] |
```

Only create a separate `.md` file for patents that need detailed claim analysis or are directly relevant to your novelty arguments.

### `ip-drafts/` Naming Convention

```
ip-drafts/YYYY-MM-DD_topic.md
```

Examples:
- `ip-drafts/2026-04-15_prior-art_[topic].md`
- `ip-drafts/2026-04-15_invention-disclosure_[concept].md`

---

## Rules for All Agents

1. **Read `CLAUDE.md` first.** Format standards, source verification, and naming conventions live there.
2. **Read `engineering-log/INDEX.md` to orient.** Master index of all design problems.
3. **Never commit to `master`.** Always branch and PR.
4. **Stay in your user's primary directories** (see `CLAUDE.md` Team Collaboration). Note in the PR if you edit outside your area.
5. **Follow the source verification policy.** Don't cite sources as verified unless you've read the actual content this session.
6. **Don't disclose IP externally.** Everything in this repo is internal unless the project's license says otherwise.
