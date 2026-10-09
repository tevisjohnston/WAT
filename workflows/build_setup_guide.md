# Build the Affiliate Theme SETUP-GUIDE.pdf

## Objective

Produce the buyer-facing `SETUP-GUIDE.pdf` and the `affiliate-theme.zip` it tells buyers to upload, then publish both to Affiliate Market Connect's secure downloads. The guide covers the buyer path at the top of `/home/tevis/wp-dfy/wp-content/themes/affiliate-theme/CLAUDE.md`, and only that path:

download → upload → install → activate → Settings › Permalinks (Post name) → Settings › Affiliate Theme Settings (key, list token, affiliate URL) → edit and publish a landing page → Settings › Reading → edit and publish the legal pages → Settings › Privacy.

The Permalinks step (guide Step 4) was added on 2026-09-28 so buyers' pages get readable addresses before anything is published.

It does not cover VPS, DNS or Docker deployment. The stale `dfy-wordpress-website.zip` (theme v1.1.0) is a separate deliverable.

## When to rebuild

- The theme's `Version` in `style.css` changes. The cover prints it, and the zip must match it.
- Any settings-screen label, help text or error string that the guide quotes changes (`inc/affiliate-theme-funnel.php`, `inc/affiliate-theme-resend.php`, `inc/affiliate-theme-emails.php`, `inc/affiliate-theme-legal.php`, `blocks/optin-form/`).
- The buyer path in the theme's CLAUDE.md changes.
- A WordPress core update renames a screen or button that the guide quotes (for example, 7.1 says **Add Theme**, not "Add New Theme").

## Inputs

| Input | Where | Notes |
|---|---|---|
| Theme source | `/home/tevis/wp-dfy` at `HEAD` | Must be committed. The zip builder refuses a dirty theme dir. |
| Dev site | `wp-dfy-wordpress-1`, https://wp-dfy.affiliatemarketconnect.com | `affiliate-theme` active, seeded pages present, `affiliate-theme_pages_created` = 1. |
| GetResponse screen-shots | `materials/setup-guides/affiliate-theme/screen-shots/getresponse/`: nine shots of the two click paths. API key: Dashboard, Tools menu, Integrations and API, API tab, Generate API key, the `-redacted` Copy API Key box. List token: Contacts › Lists, the list's three-dot menu (1366×606), list settings. All others are 1366×563 | Supplied by hand. The guide uses only the `-redacted` copy of the API key shot. Any unredacted `screen-shot-api-key-…getresponse.png` is git-ignored and must never be committed. |
| Copy and layout | `tools/templates/setup_guide.html`, `setup_guide.css` | Edit the copy here. |

## Tools, in order

One-time setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Playwright drives the host's `/usr/bin/google-chrome` (`channel="chrome"`), so there's no `playwright install` step.

1. `.venv/bin/python tools/build_theme_zip.py` builds `deliverables/affiliate-theme.zip` from `git archive HEAD` of the theme, under an `affiliate-theme/` prefix, without `CLAUDE.md`.
2. `.venv/bin/python tools/capture_setup_screens.py [--only NAME ...]` writes `.tmp/setup-guide/screens/*.png` (2× scale).
   - It logs in with cookies minted by `wp eval` for user 1, and destroys the session token on exit. No password is needed.
   - It replaces the dev site's real list token, list name, affiliate URL, site name and page statuses in the DOM before each shot. Nothing is saved.
   - Shot 04 (Settings › Permalinks) replaces the dev site's address with `https://yoursite.com` in the structure examples and the Optional help text.
   - Loading Settings › Permalinks runs core's `flush_rewrite_rules()`, which rewrites wp-dfy's repo-root `.htaccess`. With the dev site on `/%postname%/` the file comes out unchanged. Check `git -C /home/tevis/wp-dfy status` after a capture anyway.
   - Shots 01–03 switch the dev site to `twentytwentyfive` and back. The tool checks the seed flag first, then checks that the stylesheet and the page list are unchanged. If it ever reports "dev site not restored", run `wp theme activate affiliate-theme` and compare `wp post list --post_type=page`.
3. **The API key shot is already redacted.** The committed `screen-shot-api-key-email-marketing-software-getresponse-redacted.png` is the redacted copy, so skip this step. Redact again only if GetResponse's API key shot is replaced. A hand-drawn scribble is not enough: the first supplied shot still showed the key's first 8 characters and GetResponse's masked `lb9…yl6` row. Paint over the whole key field and the masked row of the new unredacted shot, then view the result before building:

   ```bash
   G=materials/setup-guides/affiliate-theme/screen-shots/getresponse; IN=$G/screen-shot-api-key-email-marketing-software-getresponse.png
   .venv/bin/python tools/redact_image.py "$IN" .tmp/setup-guide/gr/step1.png --fill '#ffffff' --box '436,299,414,38:••••••••••••••••••••••••••••••••'
   .venv/bin/python tools/redact_image.py .tmp/setup-guide/gr/step1.png "${IN%.png}-redacted.png" --box 60,369,112,22
   ```

   The box coordinates fit the 1366×563 shot supplied on 2026-09-27. A new screenshot needs new boxes. The second box's fill is sampled from the pixel to its left, so it matches the dimmed background.
4. `.venv/bin/python tools/mark_getresponse_shots.py` crops the GetResponse shots and draws the same red boxes and badges as the WordPress shots, into `.tmp/setup-guide/screens/gr-*.png`. The crops and marks are measured in source pixels on the 2026-09-28 shots. The tool stops on any shot that isn't the size it was measured on (1366×563; the three-dot menu shot is 1366×606, set in `SIZES`), and a replaced shot of the same size still needs its numbers checked. The list-token mark has no badge on purpose: a badge there covers the start of "List token:".
5. `.venv/bin/python tools/build_setup_guide.py [--draft]` writes `deliverables/SETUP-GUIDE.pdf`. It fails on any missing image. `--draft` only lets the GetResponse screen-shots be missing, and stamps DRAFT on every page.

## Verification (all must pass before publishing)

1. **Zip:** `unzip -l deliverables/affiliate-theme.zip` shows `affiliate-theme/style.css` one level down and no `CLAUDE.md`. The file list equals `git ls-tree -r --name-only HEAD:wp-content/themes/affiliate-theme` minus CLAUDE.md, and `php -l` passes on every PHP file extracted to `.tmp/`. `zipinfo deliverables/affiliate-theme.zip` shows `drwxr-xr-x` on every folder and `-rw-r--r--` on every file. Mode `?---------` or `?rw-------` means the builder copied git archive's empty MS-DOS attributes again; buyers who unzip that on a Mac get folders they can't open.
2. **Screens:** open every PNG, including the `gr-*` crops and a 150-dpi render of the PDF page holding the GetResponse click path (page 8). Check that no character of the API key shows. In the WordPress shots, check for no real list token, list name, affiliate URL or site name. (The GetResponse list-token shot shows the real token on purpose: a token is not a credential without the key.) Also check that no modal or admin notice covers a marked control.
3. **Labels:** every UI string the guide quotes is grepped against the theme source or WordPress core. Any `MISSING` means the guide is wrong. Add a row whenever the guide quotes a new string, and remove a row when the guide stops quoting it. `A static page` is not in this list: core wraps "static page" in a link, so check it against the Reading screen-shot instead. GetResponse's labels (`Tools`, `Connect`, `Integrations and API`, `API`, `Generate API key`, `Generate`, `Copy`, `Contacts`, `Lists`, `Settings`, `List token:`, `List name`, `List ID`) can't be grepped, so check them against the supplied shots. GetResponse now says "Integrations and API", and since theme 1.2.6 the theme's settings screen and its rejected-key message do too.

   ```bash
   T=/home/tevis/wp-dfy/wp-content/themes/affiliate-theme; W=/home/tevis/wp-dfy
   while IFS='|' read -r label where; do where=$(eval echo "$where")
     grep -rqF -- "$label" $where || echo "MISSING $label"; done <<'EOF'
   Affiliate Theme Settings|$T/inc
   GetResponse API key|$T/inc
   GetResponse list token|$T/inc
   Check list|$T/inc
   Affiliate redirect URL|$T/inc
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
   Permalink structure|$W/wp-admin/options-permalink.php
   Post name|$W/wp-admin/options-permalink.php
   Custom Structure|$W/wp-admin/options-permalink.php
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
- **The Reading screen's Homepage dropdown lists only published pages.** That is why the guide publishes the landing page (Step 6) before Settings › Reading (Step 7).
- **A native `<select>` popup can't be screen-shotted.** The privacy shot redraws the list as a list box (`size = options.length`). In a buyer's dropdown, the "checkmark" is the currently selected entry, which is WordPress's own draft (ID 3 on the dev site).
- **Settings › Privacy's link text depends on the page's status.** It reads "Edit or **view**" for a published page and "Edit or **preview**" for a draft (`options-privacy.php`). The guide uses this as its "did you pick the right one" check.
- **A Site Editor save shadows the theme's template files.** If a template or part looks wrong in a shot, check `wp post list --post_type=wp_template_part` for an override.
- **Chrome embeds the variable fonts as Type 3.** Poppler prints "Bad bounding box in Type 3 glyph" warnings. They're harmless, and the text renders and extracts correctly.
- **The theme's `screenshot.png` (1200×900) arrived in wp-dfy commit `63c1940`.** Its card on the Themes screen (shot 03) shows the landing page. An older zip without it shows a blank checkerboard.
- **Page 7 (Step 5) has no slack.** Its last item, "Click Save Changes.", ends at the bottom margin. Anything that makes the page taller, even a line 0.75pt taller because it gained a `.ui` span, pushes that item onto page 8 and slices its red badge in two. After any Step 5 copy edit, check that `pdftotext -f 7 -l 7` still ends with "Click Save Changes."
- **A host Python upgrade breaks `.venv`.** Its `python3` symlinks to `/usr/bin/python3`, so when that moved from 3.12 to 3.14 (found 2026-10-02) the packages in `lib/python3.12/` vanished and the capture tool failed with `No module named 'playwright'`. Rebuild it: `rm -rf .venv` then rerun the one-time setup.
- **The zip must stay under 2 MB (2,097,152 bytes).** That is PHP's default `upload_max_filesize`, which WordPress uses as its upload limit, so a bigger zip won't install on a host left at the defaults. The troubleshooting entry for "The link you followed has expired." also says "under 2 MB". Check `stat -c %s deliverables/affiliate-theme.zip` on every rebuild. Theme 1.4.1 grew the zip from 1.15 MB to 1,721,299 bytes, almost all of it `emails/landing-3/guide.pdf`, which leaves about 370 KB of headroom.
- **Selecting a Permalinks radio fills the Custom Structure box** (`wp-admin/js/common.js`), so Post name shows `/%postname%/` there. The guide quotes that.
