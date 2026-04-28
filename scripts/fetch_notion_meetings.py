#!/usr/bin/env python3
"""
Fetch meeting notes from Notion and save to meeting-notes/.
Zero LLM tokens — all content goes straight from API to disk.

Each meeting becomes a folder:
    meeting-notes/YYYY-MM-DD/
    ├── README.md       ← index of files in this meeting folder
    ├── summary.md      ← action items, topics, decisions (small, high-value)
    ├── notes.md        ← handwritten notes (small)
    └── transcript.md   ← full transcript (large, reference only)

Usage:
    python3 scripts/fetch_notion_meetings.py --list
    python3 scripts/fetch_notion_meetings.py --fetch-new
    python3 scripts/fetch_notion_meetings.py --fetch <page_id>
    python3 scripts/fetch_notion_meetings.py --fetch-all

Requires NOTION_API_KEY env var (integration token starting with ntn_).

============================================================================
SETUP (one-time):
============================================================================

1. Create a Notion integration:
   - Go to https://www.notion.so/profile/integrations
   - Click "+ New integration"
   - Give it a name (e.g., "Engineering Log Sync"), choose your workspace
   - Set type to "Internal"
   - Copy the "Internal Integration Token" (starts with `ntn_`)

2. Share the database with your integration:
   - Open the Notion database that holds your meeting notes
   - Click the "..." menu → "Connections" → add your integration

3. Find your data source ID:
   - Open the database in Notion
   - Click "..." → "Copy link to view"
   - The URL looks like: https://notion.so/workspace/DATABASE_ID?v=...
   - The DATABASE_ID is a 32-character hex string
   - Format it as 8-4-4-4-12 with hyphens, paste into DATA_SOURCE_ID below
     (e.g., "abcdef12-3456-7890-abcd-ef1234567890")

   Or programmatically:
     curl -X POST https://api.notion.com/v1/search \\
       -H "Authorization: Bearer $NOTION_API_KEY" \\
       -H "Notion-Version: 2026-03-11" \\
       -H "Content-Type: application/json" \\
       -d '{"filter": {"property": "object", "value": "database"}}'

4. Customize the filter (PROJECT_FILTER below):
   - If your meeting notes have a "Project" select property, set the value here
   - If not, remove the filter or change it to match your schema
   - Update the title-keyword filter in query_meetings() if needed

5. Set the env var:
   export NOTION_API_KEY="ntn_your_token_here"
   (Add to your shell profile to persist.)

============================================================================
"""

import os
import sys
import json
import re
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime
from pathlib import Path

API_BASE = "https://api.notion.com/v1"
API_VERSION = "2026-03-11"

# ─── CUSTOMIZE THESE ──────────────────────────────────────────────────────
# Your Notion database ID (8-4-4-4-12 hex format). See SETUP step 3.
DATA_SOURCE_ID = "REPLACE-WITH-YOUR-DATABASE-ID"

# Filter applied when querying the database. Set to None to fetch all rows.
# Default: filter by a "Project" select property. Adjust to match your schema.
PROJECT_FILTER = {
    "property": "Project",
    "select": {"equals": "REPLACE-WITH-YOUR-PROJECT-NAME"},
}

# Title keywords used to identify meeting pages within the filtered set.
# Pages whose title contains ALL of these (case-insensitive) are included.
TITLE_KEYWORDS = ["meeting", "note"]
# ──────────────────────────────────────────────────────────────────────────

MEETING_NOTES_DIR = Path(__file__).parent.parent / "meeting-notes"


def api_request(method, path, body=None):
    """Make a Notion API request."""
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        print("ERROR: NOTION_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        if e.code == 429:
            retry_after = int(e.headers.get("Retry-After", 2))
            print(f"  Rate limited, waiting {retry_after}s...", file=sys.stderr)
            time.sleep(retry_after)
            return api_request(method, path, body)
        body_text = e.read().decode()
        print(f"ERROR {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)


def query_meetings():
    """Query database for pages matching the project filter and title keywords."""
    if DATA_SOURCE_ID.startswith("REPLACE"):
        print("ERROR: Set DATA_SOURCE_ID at the top of this script.", file=sys.stderr)
        print("       See the SETUP section in the docstring.", file=sys.stderr)
        sys.exit(1)

    results = []
    body = {"page_size": 100}
    if PROJECT_FILTER:
        body["filter"] = PROJECT_FILTER

    while True:
        data = api_request("POST", f"data_sources/{DATA_SOURCE_ID}/query", body)
        for page in data.get("results", []):
            props = page.get("properties", {})
            title_arr = props.get("Name", {}).get("title", [])
            title = "".join(t.get("plain_text", "") for t in title_arr)
            title_lower = title.lower()
            if all(kw in title_lower for kw in TITLE_KEYWORDS):
                results.append({
                    "id": page["id"],
                    "title": title,
                    "created": page.get("created_time", ""),
                })
        if not data.get("has_more"):
            break
        body["start_cursor"] = data["next_cursor"]
    return results


def extract_date_from_title(title, created_time=""):
    """Parse meeting date from title like 'March 8 Meeting notes'."""
    patterns = [
        r"(\w+ \d{1,2},? \d{4})",
        r"(\d{4}-\d{2}-\d{2})",
    ]
    for pat in patterns:
        m = re.search(pat, title)
        if m:
            for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(m.group(1), fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue

    m = re.search(r"(\w+)\s+(\d{1,2})", title)
    if m:
        month_str, day_str = m.group(1), m.group(2)
        year = created_time[:4] if created_time else str(datetime.now().year)
        for fmt in ("%B", "%b"):
            try:
                month = datetime.strptime(month_str, fmt).month
                return f"{year}-{month:02d}-{int(day_str):02d}"
            except ValueError:
                continue

    if created_time:
        return created_time[:10]
    return datetime.now().strftime("%Y-%m-%d")


def fetch_blocks_recursive(block_id, depth=0):
    """Recursively fetch all child blocks and convert to markdown lines."""
    lines = []
    start_cursor = None
    while True:
        path = f"blocks/{block_id}/children?page_size=100"
        if start_cursor:
            path += f"&start_cursor={start_cursor}"
        data = api_request("GET", path)

        for block in data.get("results", []):
            block_type = block.get("type", "")
            block_data = block.get(block_type, {})
            rich_text = block_data.get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_text)

            if block_type == "heading_1":
                lines.append(f"\n# {text}\n")
            elif block_type == "heading_2":
                lines.append(f"\n## {text}\n")
            elif block_type == "heading_3":
                lines.append(f"\n### {text}\n")
            elif block_type == "paragraph":
                if text.strip():
                    lines.append(f"{text}\n")
                else:
                    lines.append("\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "bulleted_list_item":
                indent = "  " * depth
                lines.append(f"{indent}- {text}\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "numbered_list_item":
                indent = "  " * depth
                lines.append(f"{indent}1. {text}\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "to_do":
                checked = block_data.get("checked", False)
                mark = "x" if checked else " "
                lines.append(f"- [{mark}] {text}\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "toggle":
                lines.append(f"\n**{text}**\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "divider":
                lines.append("\n---\n")
            elif block_type == "callout":
                lines.append(f"\n> {text}\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "quote":
                lines.append(f"> {text}\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))
            elif block_type == "code":
                lang = block_data.get("language", "")
                lines.append(f"\n```{lang}\n{text}\n```\n")
            else:
                if text.strip():
                    lines.append(f"{text}\n")
                if block.get("has_children"):
                    lines.extend(fetch_blocks_recursive(block["id"], depth + 1))

        if not data.get("has_more"):
            break
        start_cursor = data["next_cursor"]

    return lines


def identify_section(block_id):
    """Peek at first child to identify if this is summary, notes, or transcript."""
    data = api_request("GET", f"blocks/{block_id}/children?page_size=2")
    results = data.get("results", [])
    if not results:
        return "empty"

    first = results[0]
    first_type = first.get("type", "")
    first_data = first.get(first_type, {})
    first_text = "".join(rt.get("plain_text", "") for rt in first_data.get("rich_text", []))

    if first_type in ("heading_3", "heading_2", "heading_1") or first_type == "to_do":
        return "summary"

    if first_type == "paragraph" and len(first_text) > 200:
        return "transcript"

    if first_type == "paragraph":
        return "notes"

    return "unknown"


def fetch_page_properties(page_id):
    """Fetch page properties."""
    data = api_request("GET", f"pages/{page_id}")
    props = data.get("properties", {})
    title_arr = props.get("Name", {}).get("title", [])
    title = "".join(t.get("plain_text", "") for t in title_arr)
    return {
        "title": title,
        "created_time": data.get("created_time", ""),
    }


def fetch_and_save_meeting(page_id, force=False):
    """Fetch a meeting page and save as a folder with split files."""
    print(f"Fetching page {page_id}...")
    props = fetch_page_properties(page_id)
    title = props["title"]
    date = extract_date_from_title(title, props["created_time"])
    meeting_dir = MEETING_NOTES_DIR / date

    if meeting_dir.exists() and not force:
        print(f"  SKIP: {meeting_dir.name}/ already exists (use --fetch-all to overwrite)")
        return None

    print(f"  Fetching blocks for '{title}'...")
    page_blocks = api_request("GET", f"blocks/{page_id}/children?page_size=100")

    meeting_notes_block = None
    other_blocks = []
    for block in page_blocks.get("results", []):
        if block.get("type") == "meeting_notes":
            meeting_notes_block = block
        else:
            other_blocks.append(block)

    if not meeting_notes_block:
        print(f"  No meeting_notes block found, saving as flat file...")
        content_lines = fetch_blocks_recursive(page_id)
        meeting_dir.mkdir(parents=True, exist_ok=True)
        _write_section(meeting_dir / "summary.md", date, title, "Summary",
                       "".join(content_lines).strip())
        print(f"  SAVED: {meeting_dir.name}/summary.md")
        return meeting_dir

    meeting_title_rt = meeting_notes_block.get("meeting_notes", {}).get("title", [])
    meeting_title = "".join(rt.get("plain_text", "") for rt in meeting_title_rt).strip()

    sections_data = api_request(
        "GET", f"blocks/{meeting_notes_block['id']}/children?page_size=100"
    )
    section_blocks = sections_data.get("results", [])

    sections = {}
    for sb in section_blocks:
        if not sb.get("has_children"):
            continue
        section_type = identify_section(sb["id"])
        print(f"  Found section: {section_type} ({sb['id'][:12]}...)")
        content_lines = fetch_blocks_recursive(sb["id"])
        sections[section_type] = "".join(content_lines).strip()

    meeting_dir.mkdir(parents=True, exist_ok=True)

    readme = f"""# {date} — {meeting_title or title}

**Source:** Notion (auto-imported via fetch_notion_meetings.py)
**Date:** {date}

| File | Contents | Size |
|------|----------|------|
"""
    files_written = []

    if "summary" in sections and sections["summary"]:
        _write_section(meeting_dir / "summary.md", date, meeting_title or title,
                       "Summary", sections["summary"])
        size = len(sections["summary"])
        readme += f"| [summary.md](summary.md) | Action items, decisions, topic summaries | {size:,} chars |\n"
        files_written.append(("summary.md", size))

    if "notes" in sections and sections["notes"]:
        _write_section(meeting_dir / "notes.md", date, meeting_title or title,
                       "Notes", sections["notes"])
        size = len(sections["notes"])
        readme += f"| [notes.md](notes.md) | Handwritten meeting notes | {size:,} chars |\n"
        files_written.append(("notes.md", size))

    if "transcript" in sections and sections["transcript"]:
        _write_section(meeting_dir / "transcript.md", date, meeting_title or title,
                       "Transcript", sections["transcript"])
        size = len(sections["transcript"])
        readme += f"| [transcript.md](transcript.md) | Full meeting transcript | {size:,} chars |\n"
        files_written.append(("transcript.md", size))

    if other_blocks:
        other_lines = []
        for block in other_blocks:
            block_type = block.get("type", "")
            block_data = block.get(block_type, {})
            rich_text = block_data.get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_text)
            if text.strip():
                other_lines.append(f"{text}\n")
        if other_lines:
            other_content = "".join(other_lines).strip()
            _write_section(meeting_dir / "other.md", date, meeting_title or title,
                           "Other Content", other_content)
            size = len(other_content)
            readme += f"| [other.md](other.md) | Additional page content | {size:,} chars |\n"
            files_written.append(("other.md", size))

    (meeting_dir / "README.md").write_text(readme)

    for fname, size in files_written:
        print(f"  SAVED: {meeting_dir.name}/{fname} ({size:,} chars)")
    print(f"  SAVED: {meeting_dir.name}/README.md")
    return meeting_dir


def _write_section(filepath, date, title, section_name, content):
    """Write a section file with a standard header."""
    header = f"""# {title} — {section_name}

**Date:** {date}
**Section:** {section_name}

---

"""
    filepath.write_text(header + content + "\n")


def list_meetings():
    """List meetings and their status (new vs existing)."""
    meetings = query_meetings()

    existing_dates = set()
    if MEETING_NOTES_DIR.exists():
        for item in MEETING_NOTES_DIR.iterdir():
            if item.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", item.name):
                existing_dates.add(item.name)

    print(f"Found {len(meetings)} meeting notes in Notion:\n")
    for m in sorted(meetings, key=lambda x: x.get("created", "")):
        date = extract_date_from_title(m["title"], m["created"])
        status = "EXISTS" if date in existing_dates else "NEW"
        print(f"  [{status}] {date} — {m['title']} ({m['id'][:8]}...)")
    return meetings


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "--list":
        list_meetings()

    elif cmd == "--fetch-new":
        meetings = query_meetings()
        existing_dates = set()
        if MEETING_NOTES_DIR.exists():
            for item in MEETING_NOTES_DIR.iterdir():
                if item.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", item.name):
                    existing_dates.add(item.name)

        new_count = 0
        for m in meetings:
            date = extract_date_from_title(m["title"], m["created"])
            if date not in existing_dates:
                fetch_and_save_meeting(m["id"])
                new_count += 1
        if new_count == 0:
            print("No new meetings to fetch.")
        else:
            print(f"\nFetched {new_count} new meeting(s).")

    elif cmd == "--fetch" and len(sys.argv) > 2:
        page_id = sys.argv[2]
        fetch_and_save_meeting(page_id, force=True)

    elif cmd == "--fetch-all":
        meetings = query_meetings()
        for m in meetings:
            fetch_and_save_meeting(m["id"], force=True)
        print(f"\nFetched {len(meetings)} meeting(s).")

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
