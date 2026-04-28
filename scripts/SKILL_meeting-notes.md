---
name: meeting-notes
description: "Fetch meeting notes from Notion and save to the repo. Use when the user says: /meeting-notes, 'pull meeting notes', 'get the meeting notes from Notion', 'fetch meeting transcript', 'sync meeting notes', 'download meeting notes', or references importing Notion meeting content. Also use when the user mentions a specific meeting date and wants the notes pulled in."
---

# Fetch Meeting Notes from Notion

> **This file is a reference template.** To install as a Claude Code skill, copy it to `~/.claude-self/skills/meeting-notes/SKILL.md` (or your equivalent skills directory). The repo itself only ships the Python script at `scripts/fetch_notion_meetings.py`.

This skill uses a Python script that calls the Notion REST API directly to fetch meeting notes and save them to `meeting-notes/`. Content goes straight from API to disk — zero LLM tokens for the heavy content.

## Prerequisites

- `NOTION_API_KEY` env var must be set (Notion integration token starting with `ntn_`)
- The script is at `scripts/fetch_notion_meetings.py` in the repo
- The `DATA_SOURCE_ID` and `PROJECT_FILTER` constants at the top of the script must be customized for the user's Notion database

If `NOTION_API_KEY` is not set, tell the user:
> Set your Notion API key: `export NOTION_API_KEY="ntn_your_token_here"`
> Or add it to your shell profile so it persists across sessions.

If `DATA_SOURCE_ID` still shows the placeholder, tell the user to follow the SETUP section in the script's docstring (creates the integration, finds the database ID, customizes the filter).

## Workflow

### Step 1: List available meetings

```bash
NOTION_API_KEY="$NOTION_API_KEY" python3 scripts/fetch_notion_meetings.py --list
```

This queries the Notion database and shows which meetings already have files in `meeting-notes/` vs. which are new.

Show the user the output and ask what they want to fetch.

### Step 2: Fetch meetings

**Fetch only new meetings** (not already in the repo):
```bash
NOTION_API_KEY="$NOTION_API_KEY" python3 scripts/fetch_notion_meetings.py --fetch-new
```

**Fetch a specific meeting** by page ID:
```bash
NOTION_API_KEY="$NOTION_API_KEY" python3 scripts/fetch_notion_meetings.py --fetch <page_id>
```

**Fetch all meetings** (overwrites existing files):
```bash
NOTION_API_KEY="$NOTION_API_KEY" python3 scripts/fetch_notion_meetings.py --fetch-all
```

### Step 3: Report results

Tell the user which files were created/updated and their sizes. The script prints this as it runs.

### Step 4: Handle merge cases

If the user has existing hand-written meeting notes (agendas, prep briefs) alongside the Notion import, suggest renaming the existing file (e.g., `2026-02-22_prep.md` stays, Notion import goes to `meeting-notes/2026-02-22/`).

## How the script works

The script (`scripts/fetch_notion_meetings.py`) does everything without Claude:
1. Queries the Notion database (configured via `DATA_SOURCE_ID` and `PROJECT_FILTER`)
2. Filters results to pages whose title matches `TITLE_KEYWORDS`
3. Recursively fetches all blocks from each page via the Notion blocks API
4. Converts blocks to markdown (headings, lists, to-dos, paragraphs, etc.)
5. Splits Notion `meeting_notes` blocks into `summary.md`, `notes.md`, `transcript.md`
6. Extracts the date from the page title
7. Writes to `meeting-notes/YYYY-MM-DD/` with a standard header on each file

All content transfer happens via Python `urllib` — no LLM tokens consumed for the actual meeting content.
