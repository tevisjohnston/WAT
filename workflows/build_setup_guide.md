# Build the Affiliate Theme SETUP-GUIDE.pdf

## Objective

Produce the buyer-facing `SETUP-GUIDE.pdf` and the `affiliate-theme.zip` it tells buyers to upload, then publish both to Affiliate Market Connect's secure downloads. The guide covers the buyer path at the top of `/home/tevis/wp-dfy/wp-content/themes/affiliate-theme/CLAUDE.md`, and only that path:

download → upload → install → activate → Settings › Affiliate Theme Settings (key, list token, affiliate URL) → edit and publish a landing page → Settings › Reading → edit and publish the legal pages → Settings › Privacy.

It does not cover VPS, DNS or Docker deployment. The stale `dfy-wordpress-website.zip` (theme v1.1.0) is a separate deliverable.

## When to rebuild

- The theme's `Version` in `style.css` changes. The cover prints it, and the zip must match it.
- Any settings-screen label, help text or error string that the guide quotes changes (`inc/affiliate-theme-getresponse.php`, `inc/affiliate-theme-legal.php`, `blocks/optin-form/`).
- The buyer path in the theme's CLAUDE.md changes.
- A WordPress core update renames a screen or button that the guide quotes (for example, 7.1 says **Add Theme**, not "Add New Theme").

## Inputs

| Input | Where | Notes |
|---|---|---|
| Theme source | `/home/tevis/wp-dfy` at `HEAD` | Must be committed. The zip builder refuses a dirty theme dir. |
| Dev site | `wp-dfy-wordpress-1`, https://wp-dfy.affiliatemarketconnect.com | `affiliate-theme` active, seeded pages present, `affiliate-theme_pages_created` = 1. |
| GetResponse screenshots | `Screenshots-GetResponse-API/Screenshot-1-GetResponse-API-Key.png`, `Screenshot-2-GetResponse-List-Token.png` | Supplied by hand. **Blur or crop the real API key before saving.** These files are committed. |
| Copy and layout | `tools/templates/setup_guide.html`, `setup_guide.css` | Edit the copy here. |

## Tools, in order

One-time setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Playwright drives the host's `/usr/bin/google-chrome` (`channel="chrome"`), so there's no `playwright install` step.

1. `.venv/bin/python tools/build_theme_zip.py` builds `deliverables/affiliate-theme.zip` from `git archive HEAD` of the theme, under an `affiliate-theme/` prefix, without `CLAUDE.md`.
2. `.venv/bin/python tools/capture_setup_screens.py [--only NAME ...]` writes `.tmp/setup-guide/screens/*.png` (2× scale).
   - It logs in with cookies minted by `wp eval` for user 1, and destroys the session token on exit. No password is needed.
   - It replaces the dev site's real list token, list name, affiliate URL, site name and page statuses in the DOM before each shot. Nothing is saved.
   - Shots 01–03 switch the dev site to `twentytwentyfive` and back. The tool checks the seed flag first, then checks that the stylesheet and the page list are unchanged. If it ever reports "dev site not restored", run `wp theme activate affiliate-theme` and compare `wp post list --post_type=page`.
3. `.venv/bin/python tools/build_setup_guide.py [--draft]` writes `deliverables/SETUP-GUIDE.pdf`. It fails on any missing image. `--draft` only lets the two GetResponse screenshots be missing, and stamps DRAFT on every page.

## Verification (all must pass before publishing)

1. **Zip:** `unzip -l deliverables/affiliate-theme.zip` shows `affiliate-theme/style.css` one level down and no `CLAUDE.md`. The file list equals `git ls-tree -r --name-only HEAD:wp-content/themes/affiliate-theme` minus CLAUDE.md, and `php -l` passes on every PHP file extracted to `.tmp/`.
2. **Screens:** open every PNG. Check that there's no real token, list name, affiliate URL or site name, and no modal or admin notice covering a marked control.
3. **Labels:** every UI string the guide quotes is grepped against the theme source or WordPress core. Any `MISSING` means the guide is wrong. Add a row whenever the guide quotes a new string. `A static page` is not in this list: core wraps "static page" in a link, so check it against the Reading screenshot instead.

   ```bash
   T=/home/tevis/wp-dfy/wp-content/themes/affiliate-theme; W=/home/tevis/wp-dfy
   while IFS='|' read -r label where; do where=$(eval echo "$where")
     grep -rqF -- "$label" $where || echo "MISSING $label"; done <<'EOF'
   Affiliate Theme Settings|$T/inc
   GetResponse API key|$T/inc
   GetResponse list token|$T/inc
   Check list|$T/inc
   Affiliate redirect URL|$T/inc
   Success message|$T/inc
   GetResponse accepted this list.|$T/inc
   Your landing pages|$T/inc
   Your legal pages|$T/inc
   If you add analytics, advertising or cookies|$T/inc
   Opt-in form is not ready.|$T/blocks
   That does not look like a GetResponse API key.|$T/inc
   GetResponse rejected the API key.|$T/inc
   GetResponse did not accept that list token.|$T/inc
   The affiliate redirect URL is not a usable address.|$T/inc
   Something went wrong. Please try again.|$T/inc
   Please try again in a moment.|$T/inc
   Button text|$T/blocks
   Email field label|$T/blocks
   Ask for a first name|$T/blocks
   Name field label|$T/blocks
   Theme installed successfully.|$W/wp-admin/includes
   The theme is missing the %s stylesheet.|$W/wp-admin/includes
   The link you followed has expired.|$W/wp-includes
   This theme is already installed.|$W/wp-admin/includes
   Replace installed with uploaded|$W/wp-admin/includes
   Upload Theme|$W/wp-admin
   Install Now|$W/wp-admin
   Your homepage displays|$W/wp-admin/options-reading.php
   Change your Privacy Policy page|$W/wp-admin
   Use This Page|$W/wp-admin
   Are you ready to publish?|$W/wp-includes/js/dist
   EOF
   ```

   The seven placeholders must be spelled exactly as they are in `inc/affiliate-theme-legal.php`.
4. **PDF:** `pdfinfo` (Letter), `pdffonts` (Archivo and Newsreader embedded), then `pdftoppm -r 90` and review every page for widowed headings, stranded figures and overflow.

## Publish

```bash
D=/home/tevis/affiliatemarketconnect.com/wp-content/uploads/amc-secure-assets
install -m 0644 -o root -g root deliverables/SETUP-GUIDE.pdf deliverables/affiliate-theme.zip "$D"/
docker exec affiliatemarketconnectcom-wordpress-1 test -r /var/www/html/wp-content/uploads/amc-secure-assets/SETUP-GUIDE.pdf && echo readable
```

Members download them through `/wp-json/amc/v1/download?file=SETUP-GUIDE.pdf` and `?file=affiliate-theme.zip`. The download buttons on the Domain + Web Hosting step are added by hand in the affiliate-market-connect theme. This workflow doesn't touch that theme. Those files are tracked in the affiliatemarketconnect.com repo, so commit there only when asked.

## Known quirks

- **The block editor never goes network-idle** because of heartbeat polling. Wait on `wp.data` state, not on `networkidle`.
- **WP-CLI `post list --name=`** does not find draft pages. Use `get_page_by_path()` in `wp eval`.
- **The Reading screen's Homepage dropdown lists only published pages.** That is why the guide publishes the landing page (Step 5) before Settings › Reading (Step 6).
- **A native `<select>` popup can't be screenshotted.** The privacy shot redraws the list as a list box (`size = options.length`). In a buyer's dropdown, the "checkmark" is the currently selected entry, which is WordPress's own draft (ID 3 on the dev site).
- **Settings › Privacy's link text depends on the page's status.** It reads "Edit or **view**" for a published page and "Edit or **preview**" for a draft (`options-privacy.php`). The guide uses this as its "did you pick the right one" check.
- **A Site Editor save shadows the theme's template files.** If a template or part looks wrong in a shot, check `wp post list --post_type=wp_template_part` for an override.
- **Chrome embeds the variable fonts as Type 3.** Poppler prints "Bad bounding box in Type 3 glyph" warnings. They're harmless, and the text renders and extracts correctly.
- **The Affiliate Theme has no `screenshot.png`,** so its card on the Themes screen shows a blank checkerboard (shot 03).
