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
- `tools/templates/` — HTML/CSS that `build_affiliate_theme_guide.py`, `build_lead_guide.py` and `build_blueprint.py` fill and print to PDF (copy is edited here, not in Python)
- `materials/guides/affiliate-theme/screenshots/`: the owner's hand-supplied shots for the Affiliate Theme Guide, in `resend/`, `cloudflare/` and `affiliate-market-connect/` (the members page Step 1 shows; all read by `mark_resend_shots.py`; only the `-redacted` copies of the API key list shots are committed and read) plus `affiliate-theme-settings/` and `affiliate-theme/`, and beside them `affiliate-theme-settings-copy/affiliate-theme-settings-copy.md`, the owner's source text for the guide (written against an older settings screen, so check each string against 2.0.0). `materials/guides/resend-email-automation/` is an empty placeholder, on disk only. dc169e3 deleted the GetResponse screen-shots that used to sit in `.../affiliate-theme/screen-shots/getresponse/` and `getresponse-email-automation/`. They survive only in git history (`git show 1ec2bd4:<path>`).
- `materials/lead-magnets/The-Affiliate-Marketing-Blueprint/` — the old Gamma export of the 7figure lead magnet (reference only) and `images/`, the illustrations `build_blueprint.py` uses
- `materials/fonts/fraunces/` — Fraunces (OFL) for the blueprint: the 7figure theme declares it but never loads it
- `materials/fonts/inter/` — Inter (OFL), which `mark_resend_shots.py` uses to write `yoursite.com` over the test domain in the Resend and Cloudflare shots
- `materials/fonts/newsreader/` — Newsreader (OFL), used by the blueprint for its display face's lowercase f only, in place of Fraunces' hooked f

## What exists today

Three workflows. Read the relevant one before touching any tool; their rebuild triggers, verification steps and "Known quirks" are not repeated here.

- `workflows/build_affiliate_theme_guide.md` builds the two buyer deliverables for the `wp-test` affiliate theme — `deliverables/affiliate-theme.zip` and `deliverables/affiliate-theme-guide.pdf` — and publishes them to `affiliatemarketconnect.com`'s secure downloads.
- `workflows/build_lead_guide.md` prints `guide.pdf`, the guide the theme's Long Form landing page promises, and copies it into the theme as `assets/lead-magnets/landing-3-guide.pdf`.
- `workflows/build_blueprint.md` builds `deliverables/The-Affiliate-Marketing-Blueprint.pdf`, the lead magnet that 7figure's `WelcomeEmail` links from `wp-content/uploads/lead-magnets/`. Copying it to the 7figure site, and committing it there, is a manual step after the build.

### Current state: Resend 2.0.0, published 2026-11-13

The wp-test theme's `main` is at **2.0.0** (check `style.css`): branch `resend-2.0.0`, which brought in Resend phase by phase, was fast-forwarded into `main` on 2026-10-25. 1.5.0 had removed GetResponse and deleted `emails/`, which held the landing-3 email package and `guide.pdf`; 2.0.0 puts both back in Resend's form. On 2026-11-06 the owner declared it finished, and `deliverables/` got the 2.0.0 `affiliate-theme.zip` (1,754,721 bytes, wp-test `40e0c62`; rebuilt 2026-11-10 at `67be050`, which renamed the settings field "Affiliate redirect URL" to "Affiliate link", 1,754,705 bytes; rebuilt 2026-11-11 at `4e64379`, whose privacy add-on placeholder is `[PROVIDER NAME]`, 1,754,722 bytes, and again at `ba37526`, whose legal placeholders are all caps (`[YOUR BUSINESS NAME]` and so on), 1,754,755 bytes; rebuilt 2026-11-13 at `6590197`, Centered email 2 and Split email 5 copy, 1,754,756 bytes) and `affiliate-theme-guide.pdf` (27 pages; 24 after the owner trimmed the copy on 2026-11-11), the guide rewritten for 2.0.0 (`tools/templates/affiliate_theme_guide.html`), with the WordPress shots from wp-guide, the Resend and Cloudflare shots marked by `mark_resend_shots.py`, and the workflow's label grep checking the 2.0.0 strings. The tools read whatever wp-test has checked out.

- **Published 2026-11-13.** `amc-secure-assets/` holds the 2.0.0 `affiliate-theme.zip` and `affiliate-theme-guide.pdf` (byte-identical to `deliverables/`). 1.4.1's `SETUP-GUIDE.pdf` stays there until the Domain + Web Hosting step's saved guide button is pointed at `?file=affiliate-theme-guide.pdf` (owner), then it is removed. A later theme change is committed in wp-test with a `Version` bump, rebuilt into `deliverables/` under the workflow's triggers and published again. A zip for testing on wp-guide goes to `.tmp/wp-guide/affiliate-theme.zip` (`build_theme_zip.py --out`), and a draft guide to `.tmp/affiliate-theme-guide/affiliate-theme-guide-draft.pdf` (`build_affiliate_theme_guide.py --draft --out`).
- **`build_lead_guide.py` copies the guide into the theme as `assets/lead-magnets/landing-3-guide.pdf`**, creating the folder. Theme 2.0.0's Long Form email 1 links it there. Run the tool while wp-test has `main` (2.0.0) checked out.
- `build_affiliate_theme_guide.md` describes the 2.0.0 pipeline; how 1.4.1 was built with GetResponse is in git history (WAT before 2026-10-31). `build_lead_guide.md` has a **Status** section saying where the guide ships.
- Commit 1ec2bd4 names "affiliate-theme 2.0.0", along with `inc/affiliate-theme-resend.php` and `inc/affiliate-theme-emails.php`. Those came from the abandoned first 2.0.0 candidate (wp-dfy `backup/resend-2.0.0`, tip `6483bd4`). Branch `resend-2.0.0`, now merged, rebuilt both, so `main`'s `inc/` holds `funnel`, `legal`, `seo`, `resend` and `emails`.
- **wp-dfy hashes cited here and in the workflows** (`d62daf2`, `63c1940`, `6483bd4`) live only in the GitHub repo `tevisjohnston/wp-dfy`: the checkout at `/home/tevis/wp-dfy` has been removed. Read one with `gh api repos/tevisjohnston/wp-dfy/commits/<sha>`.

The tools reach outside this repo, so they have side effects elsewhere:
- `build_theme_zip.py` reads `git archive HEAD` of `/home/tevis/wp-test/wp-content/themes/affiliate-theme` and refuses a dirty theme dir — commit in `wp-test/` first.
- `capture_setup_screens.py` drives a live site through `docker exec ... wp` and Playwright: by default the buyer-style `wp-guide-wordpress-1` at wp-guide.affiliatemarketconnect.com (no repo; the theme is uploaded from the test zip), or `wp-test-wordpress-1` with `--site wp-test`. It mints login cookies for user 1 and briefly switches the active theme to `twentytwentyfive`. On wp-test, loading Permalinks rewrites the repo's `.htaccess`, so check `git -C /home/tevis/wp-test status` afterwards. If it reports "site not restored", run `wp theme activate affiliate-theme` in that container.
- `build_affiliate_theme_guide.py` pulls the theme's `style.css` `Version` and its `assets/fonts/` straight from the wp-test checkout.
- `build_lead_guide.py` reads the theme's fonts and its Long Form pattern (it fails unless the guide quotes that page's "What Is In The Guide" bullets word for word), and without `--no-copy` writes `assets/lead-magnets/landing-3-guide.pdf` into the wp-test theme, creating the folder (`--no-copy` builds into `.tmp/lead-guide/` only; see Current state).
- `build_blueprint.py` only reads outside the repo: Manrope from the 7figure theme's `assets/css/src/fonts/`. It never writes to the 7figure site.

The two workflows share a size budget: `affiliate-theme.zip` must stay under 2 MB (2,097,152 bytes, PHP's default upload limit), and `guide.pdf` is most of it. `build_lead_guide.py` caps only the PDF at 2 MB, so a guide that passes its own check can still push the zip over. Check `stat -c %s deliverables/affiliate-theme.zip` after every zip rebuild. The headroom at theme 1.4.1 was about 370 KB. 1.5.0 dropped the guide from the theme, and 2.0.0 puts it back in `assets/lead-magnets/`, so the budget matters again: built the way `build_theme_zip.py` builds it, 2.0.0's theme with its emails and the guide came to 1,714,080 bytes on 2026-10-19 (about 374 KB of headroom), before the rest of the Resend code went in. The built 2.0.0 zip is 1,754,372 bytes (about 343 KB of headroom).

Pipeline data flow: `capture_setup_screens.py` → `.tmp/affiliate-theme-guide/screens/NN-*.png`; `mark_resend_shots.py` (imports `MARK_JS` from the capture tool, so the red boxes match) → `.tmp/affiliate-theme-guide/screens/amc-1-download.png`, `rs-*.png` and `cf-*.png`; `build_affiliate_theme_guide.py` fills `{{CSS}}/{{FONTS}}/{{SCREENS}}/{{VERSION}}/{{DRAFT}}` in the template and fails on any missing image or unfilled token.

The crops and marks in `mark_resend_shots.py` are hard-coded pixel coordinates for specific supplied screenshots, and each `SHOTS` entry holds its source's size (the shots come at several window widths), so the tool stops on a shot of any other size. A replaced screenshot needs its numbers re-measured, even at the same size. Never commit an unredacted API-key shot. `.gitignore` now ignores `screenshot-api-key-*resend.png` in any folder; redact with `redact_image.py` and commit only the redacted copy.

Files under `materials/` are named in lowercase kebab-case, and dc169e3 moved the convention from `screen-shot` to `screenshot`. Tools hard-code these filenames (`SHOTS` in `mark_resend_shots.py`), and paths are case-sensitive, so renaming a file means editing the tool too.

## Commands

All from `/home/tevis/WAT`. Every tool uses Playwright with the host's `/usr/bin/google-chrome` (`channel="chrome"`) — no `playwright install`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # one-time; redo (rm -rf .venv first) after a host Python upgrade
.venv/bin/python tools/build_theme_zip.py [--out PATH]
.venv/bin/python tools/capture_setup_screens.py [--site wp-guide|wp-test] [--only 05-settings ...]   # re-capture single shots (default wp-guide)
.venv/bin/python tools/mark_resend_shots.py
.venv/bin/python tools/build_affiliate_theme_guide.py [--draft] [--out PATH]
.venv/bin/python tools/build_lead_guide.py [--no-copy]                      # landing-3 guide.pdf into the wp-test theme
.venv/bin/python tools/build_blueprint.py [--out PATH]                      # 7figure's lead magnet into deliverables/
.venv/bin/python tools/redact_image.py IN.png OUT.png --box x,y,w,h[:TEXT] [--fill '#rrggbb']   # one-off; the API key list shots, see the workflow's tool 3
```

The dependencies are Playwright and Pillow (`build_blueprint.py` re-encodes its images), and no current tool reads `.env` (there is no `.env.example`; dc169e3 removed it).

There are no tests or linters. Verification is the checklist in the workflow (zip listing and modes, viewing every screen-shot, the UI-label grep, `pdfinfo`/`pdffonts`/`pdftoppm` page review).

## Commits

Deliverables are committed alongside the tools that built them. Messages follow the existing style: `Added - <paths> && Modified - <paths> && Moved - <a> to <b> - <one-sentence summary, incl. theme version>`.

## Bottom Line

You sit between what I want (workflows, deliverables) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
