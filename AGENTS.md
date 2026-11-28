# WAT project instructions

WAT (Workflows, Agents, Tools) builds WordPress affiliate-engine buyer packages and PDF lead magnets. Agents coordinate Markdown SOPs in `workflows/`; Python scripts in `tools/` perform execution. This repository builds publishing artifacts; the WordPress theme source lives in neighboring repositories. Read the relevant workflow before running tools; `CLAUDE.md` provides detailed history and additional constraints.

## Layout and workflow selection

- `workflows/build_affiliate_engine_guide.md`: buyer ZIP, setup-guide screenshots/PDF, verification, and secure-download publishing.
- `workflows/build_lead_guide.md`: subscriber guide promised by the theme's Long Form landing page.
- `workflows/build_blueprint.md`: 7figure's Affiliate Marketing Blueprint lead magnet.
- `tools/templates/`: editable HTML copy and CSS layout; edit these rather than generated PDFs or copy embedded in Python.
- `materials/`: supplied screenshots, illustrations, fonts, and reference documents.
- `deliverables/`: tracked final PDFs/ZIP; `.tmp/`: ignored, regenerable HTML, images, and draft PDFs.
- Reuse existing tools first. Ask before creating or overwriting workflows; preserve their rebuild triggers and verification checklists.

## Dev environment

Run commands from `/home/tevis/WAT`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

`requirements.txt` specifies `playwright>=1.63` and `Pillow>=11`; there is no lockfile. Browser tools use the host's `/usr/bin/google-chrome` via `channel="chrome"`; no `playwright install` step. Capture requires Docker and WP-CLI in the target container. Verification uses Poppler (`pdfinfo`, `pdffonts`, `pdftoppm`, `pdftotext`), unzip/zipinfo, PHP CLI, and ImageMagick `montage`. No current tool reads `.env`.

## Build commands

Buyer package pipeline (run only the steps required by the workflow's rebuild triggers):

```bash
.venv/bin/python tools/build_theme_zip.py
.venv/bin/python tools/capture_setup_screens.py
.venv/bin/python tools/mark_resend_shots.py
.venv/bin/python tools/build_affiliate_engine_guide.py
```

ZIP and guide default to `deliverables/affiliate-engine.zip` and `deliverables/affiliate-engine-guide.pdf`. Capture defaults to the live `wp-guide` site, not the dev site.

Documented draft and targeted invocations:

```bash
.venv/bin/python tools/build_theme_zip.py --out .tmp/wp-guide/affiliate-engine.zip
.venv/bin/python tools/capture_setup_screens.py --site wp-test --only 05b-domain
.venv/bin/python tools/build_affiliate_engine_guide.py --draft --out .tmp/affiliate-engine-guide/affiliate-engine-guide-draft.pdf
.venv/bin/python tools/build_lead_guide.py --no-copy
.venv/bin/python tools/build_blueprint.py --out .tmp/blueprint/draft.pdf
```

`--draft` permits missing hand-supplied `data-rs` images only, not missing WordPress shots. `05b-domain` needs a pending domain; follow the workflow's special capture procedure rather than altering a real Resend account.

Production lead-magnet builds:

```bash
.venv/bin/python tools/build_lead_guide.py
.venv/bin/python tools/build_blueprint.py
```

Lead-guide also writes `/home/tevis/wp-test/wp-content/themes/affiliate-engine/assets/lead-magnets/landing-3-guide.pdf`; `--no-copy` avoids that cross-repo write. Blueprint defaults to `deliverables/The-Affiliate-Marketing-Blueprint.pdf`; it does not publish to the 7figure site.

## Verification (no test or lint suite)

There is no configured test runner, linter, Makefile, or CI workflow. Follow the selected workflow's full verification checklist, not just a successful build exit.

```bash
unzip -l deliverables/affiliate-engine.zip
zipinfo deliverables/affiliate-engine.zip
stat -c %s deliverables/affiliate-engine.zip
```

- ZIP: `affiliate-engine/style.css` one level down; exclude both `CLAUDE.md` and `AGENTS.md` (the builder's `EXCLUDE` is newer than the workflow's CLAUDE-only wording). Compare against the committed theme tree minus these exclusions; lint every extracted PHP file with `php -l`. Folders are 0755; ordinary files are 0644, with tracked executable modes preserved.
- ZIP must stay below 2,097,152 bytes. The ZIP builder does not enforce this; a passing lead-guide PDF size check does not guarantee the combined ZIP fits.
- PDFs: use `pdfinfo` for Letter size, `pdffonts` for embedded fonts, and render/review every page with `pdftoppm` at the workflow's specified resolution. Inspect page breaks, clipped badges, overflow, and font fallback.
- Setup guide: run the workflow's exact UI-label grep and inspect every screenshot for exposed keys, account names, real domains/addresses, and obscured controls.
- Lead guide checks the Long Form “What Is In The Guide” bullets against chapter text. Blueprint checks campaign arithmetic and displayed `data-v` values, but its email promises and PDF links still need manual review.

## Conventions and external dependencies

- Python tools use `argparse`, `pathlib`, helper functions, `main() -> int`, and `sys.exit(main())`; validation failures commonly print `ERROR:` to stderr and return 1.
- Template tokens such as `{{CSS}}`, `{{FONTS}}`, and `{{SCREENS}}` are filled by builders; unfilled tokens fail the build. Edit blueprint numeric `data-*` attributes and visible `data-v` cells together.
- Screenshot filenames generally use lowercase kebab-case. Paths and crop coordinates are hard-coded in `mark_resend_shots.py`; renames or replacement shots require updating/re-measuring entries, even at the same image size.
- Theme ZIP uses committed `HEAD` in `/home/tevis/wp-test`, refuses a dirty theme directory, and does not package working-tree edits. Other builders read the checked-out theme's fonts/source directly.
- Blueprint reads Manrope from `/home/tevis/7figure.affiliatemarketconnect.com/wp-content/themes/7_Figure_Affiliate/assets/css/src/fonts/`; Fraunces and Newsreader come from `materials/fonts/`.
- Deliverables are committed with source changes when requested. Existing messages use `Modified - <paths> - <summary>` and combine change groups with ` && `; include theme version for theme releases. Publishing and commits in neighboring repos are separate actions.

## Pitfalls

- Capture mints a user-1 session and briefly switches the live theme to `twentytwentyfive`. If it reports “site not restored,” restore `affiliate-engine` in the target container and compare the page list. After wp-test capture, check `git -C /home/tevis/wp-test status`: Permalinks can rewrite `.htaccess`.
- WordPress's editor never reaches network-idle because of heartbeat polling; wait on `wp.data` state. Site Editor saves can shadow theme template files with database overrides.
- Never commit unredacted API-key screenshots. Use `tools/redact_image.py` as described in the workflow and visually inspect the result; only redacted key-list copies are build inputs. The ignore pattern does not protect every possible filename.
- A host Python upgrade can break `.venv`; recreate it using the setup command after removing the obsolete environment.
- Poppler's “Bad bounding box in Type 3 glyph” warnings are expected for Chrome-embedded variable fonts; inspect actual rendering rather than treating those warnings alone as failure.
