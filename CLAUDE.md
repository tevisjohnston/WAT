# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go into deliverables so I can access them
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
deliverables/   # Markdown, PDF files, HTML files, zip files
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
```

**Also in this repo:**
- `tools/templates/` — HTML/CSS that `build_setup_guide.py` fills and prints to PDF (guide copy is edited here, not in Python)
- `setup-guide-edits/` — hand-supplied GetResponse screenshots the guide uses, plus `setup-guide-edits.md`, an edit list from a past revision round
- `email-automation-setup-guide/` — GetResponse screenshots only; no workflow or tool uses them yet

## What exists today

One workflow: `workflows/build_setup_guide.md`. It builds the two buyer deliverables for the `wp-dfy` affiliate theme — `deliverables/affiliate-theme.zip` and `deliverables/SETUP-GUIDE.pdf` — and publishes them to `affiliatemarketconnect.com`'s secure downloads. Read it before touching any tool; its rebuild triggers, verification steps and "Known quirks" are not repeated here.

The tools reach outside this repo, so they have side effects elsewhere:
- `build_theme_zip.py` reads `git archive HEAD` of `/home/tevis/wp-dfy/wp-content/themes/affiliate-theme` and refuses a dirty theme dir — commit in `wp-dfy/` first.
- `capture_setup_screens.py` drives the live `wp-dfy-wordpress-1` dev site through `docker exec ... wp` and Playwright: it mints login cookies for user 1, briefly switches the active theme to `twentytwentyfive`, and loading Permalinks rewrites wp-dfy's `.htaccess`. Check `git -C /home/tevis/wp-dfy status` afterwards.
- `build_setup_guide.py` pulls the theme's `style.css` `Version` and its `assets/fonts/` straight from the wp-dfy checkout.

Pipeline data flow: `capture_setup_screens.py` → `.tmp/setup-guide/screens/NN-*.png`; `mark_getresponse_shots.py` (imports `MARK_JS` from the capture tool, so the red boxes match) → `.tmp/setup-guide/screens/gr-*.png`; `build_setup_guide.py` fills `{{CSS}}/{{FONTS}}/{{SCREENS}}/{{VERSION}}/{{DRAFT}}` in the template and fails on any missing image or unfilled token.

The GetResponse crops and marks in `mark_getresponse_shots.py` and the redaction boxes in the workflow are hard-coded pixel coordinates for specific supplied screenshots. A replaced screenshot needs its numbers re-measured, even at the same size. Never commit an unredacted `Screenshot-API-key-*GetResponse.png` (git-ignored); only the `-REDACTED` copy is used.

## Commands

All from `/home/tevis/WAT`. Every tool uses Playwright with the host's `/usr/bin/google-chrome` (`channel="chrome"`) — no `playwright install`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # one-time; redo (rm -rf .venv first) after a host Python upgrade
.venv/bin/python tools/build_theme_zip.py
.venv/bin/python tools/capture_setup_screens.py [--only 05-settings ...]   # re-capture single shots
.venv/bin/python tools/mark_getresponse_shots.py
.venv/bin/python tools/build_setup_guide.py [--draft]
```

There are no tests or linters. Verification is the checklist in the workflow (zip listing and modes, viewing every screenshot, the UI-label grep, `pdfinfo`/`pdffonts`/`pdftoppm` page review).

## Commits

Deliverables are committed alongside the tools that built them. Messages follow the existing style: `Added - <paths> && Modified - <paths> && Moved - <a> to <b> - <one-sentence summary, incl. theme version>`.

## Bottom Line

You sit between what I want (workflows, deliverables) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
