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
- `tools/templates/` — HTML/CSS that `build_setup_guide.py`, `build_lead_guide.py` and `build_blueprint.py` fill and print to PDF (copy is edited here, not in Python)
- `materials/setup-guides/affiliate-theme/screen-shots/getresponse/` — the nine hand-supplied GetResponse screen-shots the setup guide uses (`mark_getresponse_shots.py` reads them)
- `materials/setup-guides/getresponse-email-automation/screen-shots/` — GetResponse screen-shots of the automation-message upload path (shot 6 is the Upload from ZIP dialog), plus `emails/` Gmail shots of landing-3 email 1 on desktop and mobile, and `emails/emails-centered/` versions of the same two shots. They set the per-email ZIP format the theme's email download follows; no tool uses them yet
- `materials/lead-magnets/The-Affiliate-Marketing-Blueprint/` — the old Gamma export of the 7figure lead magnet (reference only) and `images/`, the illustrations `build_blueprint.py` uses
- `materials/fonts/fraunces/` — Fraunces (OFL) for the blueprint: the 7figure theme declares it but never loads it
- `materials/fonts/newsreader/` — Newsreader (OFL), used by the blueprint for its display face's lowercase f only, in place of Fraunces' hooked f

## What exists today

Three workflows. Read the relevant one before touching any tool; their rebuild triggers, verification steps and "Known quirks" are not repeated here.

- `workflows/build_setup_guide.md` builds the two buyer deliverables for the `wp-dfy` affiliate theme — `deliverables/affiliate-theme.zip` and `deliverables/SETUP-GUIDE.pdf` — and publishes them to `affiliatemarketconnect.com`'s secure downloads.
- `workflows/build_lead_guide.md` prints `guide.pdf`, the guide the theme's Long Form landing page promises, straight into the theme at `emails/landing-3/guide.pdf`. The theme ships it inside the first email of its landing-3 email download (the emails themselves are theme code: see **Email sequences** in the theme's CLAUDE.md). Commit it in `wp-dfy/`, then rebuild the zip with the first workflow.
- `workflows/build_blueprint.md` builds `deliverables/The-Affiliate-Marketing-Blueprint.pdf`, the lead magnet that 7figure's `WelcomeEmail` links from `wp-content/uploads/lead-magnets/`. Copying it to the 7figure site, and committing it there, is a manual step after the build.

The tools reach outside this repo, so they have side effects elsewhere:
- `build_theme_zip.py` reads `git archive HEAD` of `/home/tevis/wp-dfy/wp-content/themes/affiliate-theme` and refuses a dirty theme dir — commit in `wp-dfy/` first.
- `capture_setup_screens.py` drives the live `wp-dfy-wordpress-1` dev site through `docker exec ... wp` and Playwright: it mints login cookies for user 1, briefly switches the active theme to `twentytwentyfive`, and loading Permalinks rewrites wp-dfy's `.htaccess`. Check `git -C /home/tevis/wp-dfy status` afterwards.
- `build_setup_guide.py` pulls the theme's `style.css` `Version` and its `assets/fonts/` straight from the wp-dfy checkout.
- `build_lead_guide.py` reads the theme's fonts and its Long Form pattern (it fails unless the guide quotes that page's "What Is In The Guide" bullets word for word), and writes `emails/landing-3/guide.pdf` into the wp-dfy theme, leaving the theme dir dirty until you commit (`--no-copy` builds into `.tmp/lead-guide/` only).
- `build_blueprint.py` only reads outside the repo: Manrope from the 7figure theme's `assets/css/src/fonts/`. It never writes to the 7figure site.

The two workflows share a size budget: `affiliate-theme.zip` must stay under 2 MB (2,097,152 bytes, PHP's default upload limit), and `guide.pdf` is most of it. `build_lead_guide.py` caps only the PDF at 2 MB, so a guide that passes its own check can still push the zip over. Check `stat -c %s deliverables/affiliate-theme.zip` after every zip rebuild. The headroom at theme 1.4.1 was about 370 KB.

Pipeline data flow: `capture_setup_screens.py` → `.tmp/setup-guide/screens/NN-*.png`; `mark_getresponse_shots.py` (imports `MARK_JS` from the capture tool, so the red boxes match) → `.tmp/setup-guide/screens/gr-*.png`; `build_setup_guide.py` fills `{{CSS}}/{{FONTS}}/{{SCREENS}}/{{VERSION}}/{{DRAFT}}` in the template and fails on any missing image or unfilled token.

The GetResponse crops and marks in `mark_getresponse_shots.py` and the redaction boxes in the workflow are hard-coded pixel coordinates for specific supplied screen-shots. A replaced screen-shot needs its numbers re-measured, even at the same size. Never commit an unredacted `screen-shot-api-key-*getresponse.png` (git-ignored); only the `-redacted` copy is used.

Files under `materials/` are named in lowercase kebab-case, and `mark_getresponse_shots.py` hard-codes each one in `SHOTS`. Paths are case-sensitive, so renaming a shot means editing `SHOTS` too.

## Commands

All from `/home/tevis/WAT`. Every tool uses Playwright with the host's `/usr/bin/google-chrome` (`channel="chrome"`) — no `playwright install`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # one-time; redo (rm -rf .venv first) after a host Python upgrade
.venv/bin/python tools/build_theme_zip.py [--out PATH]
.venv/bin/python tools/capture_setup_screens.py [--only 05-settings ...]   # re-capture single shots
.venv/bin/python tools/mark_getresponse_shots.py
.venv/bin/python tools/build_setup_guide.py [--draft] [--out PATH]
.venv/bin/python tools/build_lead_guide.py [--no-copy]                      # landing-3 guide.pdf into the wp-dfy theme
.venv/bin/python tools/build_blueprint.py [--out PATH]                      # 7figure's lead magnet into deliverables/
.venv/bin/python tools/redact_image.py IN.png OUT.png --box x,y,w,h[:TEXT] [--fill '#rrggbb']   # one-off; the workflow has the exact API-key boxes
```

The dependencies are Playwright and Pillow (`build_blueprint.py` re-encodes its images), and no current tool reads `.env` (`.env.example` holds only placeholder keys).

There are no tests or linters. Verification is the checklist in the workflow (zip listing and modes, viewing every screen-shot, the UI-label grep, `pdfinfo`/`pdffonts`/`pdftoppm` page review).

## Commits

Deliverables are committed alongside the tools that built them. Messages follow the existing style: `Added - <paths> && Modified - <paths> && Moved - <a> to <b> - <one-sentence summary, incl. theme version>`.

## Bottom Line

You sit between what I want (workflows, deliverables) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
