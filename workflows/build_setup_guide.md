# Build the Affiliate Theme SETUP-GUIDE.pdf

## Objective

Produce the buyer-facing `SETUP-GUIDE.pdf` and the `affiliate-theme.zip` it tells buyers to upload, then publish both to Affiliate Market Connect's secure downloads. The guide covers the buyer path at the top of `/home/tevis/wp-test/wp-content/themes/affiliate-theme/CLAUDE.md`, and only that path:

download → upload → install → activate → Settings › Permalinks (Post name) → Settings › Affiliate Theme Settings (key, list token, affiliate URL) → edit and publish a landing page → Settings › Reading → edit and publish the legal pages → Settings › Privacy.

The Permalinks step (guide Step 4) was added on 2026-09-28 so buyers' pages get readable addresses before anything is published.

It does not cover VPS, DNS or Docker deployment. The stale `dfy-wordpress-website.zip` (theme v1.1.0) is a separate deliverable.

## Status: on hold until the Resend work lands

The published `SETUP-GUIDE.pdf` and `affiliate-theme.zip` are theme **1.4.1**, the last GetResponse release. **Do not run this workflow against theme 1.5.0.** wp-test's `main` has been 2.0.0 since 2026-10-25, which still waits for its live run on Free and the guide rewrite. Until then only the test zip is built (`tools/build_theme_zip.py --out .tmp/wp-guide/affiliate-theme.zip`), and `deliverables/` stays at 1.4.1.

- 1.5.0 (wp-dfy `d62daf2`) removed GetResponse ahead of the move to Resend. The opt-in form shows visitors nothing, so a 1.5.0 zip would ship a funnel that collects nothing.
- 1.5.0 also drops the key, list token and Check list fields from the settings screen. In the theme's buyer path, the buyer now only pastes the affiliate URL there. The template's Step 5 still walks through the GetResponse fields.
- WAT `dc169e3` deleted the nine GetResponse screen-shots, so `mark_getresponse_shots.py` stops with `FileNotFoundError`. They are in git history (`git show 1ec2bd4:materials/setup-guides/affiliate-theme/screen-shots/getresponse/<file>`) if the 1.4.1 guide ever has to be rebuilt.

When Resend lands, rewrite Step 5 of `tools/templates/setup_guide.html` for the new settings screen. Put the hand-supplied Resend screenshots in `materials/setup-guides/affiliate-theme/screenshots/resend/`, then replace or adapt `mark_getresponse_shots.py` and re-measure every crop, mark and redaction box. Swap the provider rows of the label grep below, and update this workflow's GetResponse-specific steps and quirks. Until then, those steps describe how 1.4.1 was built.

## When to rebuild

- The theme's `Version` in `style.css` changes. The cover prints it, and the zip must match it.
- Any settings-screen label, help text or error string that the guide quotes changes (`inc/affiliate-theme-funnel.php`, `inc/affiliate-theme-legal.php`, `blocks/optin-form/`, plus whatever file the Resend integration adds).
- The buyer path in the theme's CLAUDE.md changes.
- A WordPress core update renames a screen or button that the guide quotes (for example, 7.1 says **Add Theme**, not "Add New Theme").

## Inputs

| Input | Where | Notes |
|---|---|---|
| Theme source | `/home/tevis/wp-test` at `HEAD` | Must be committed. The zip builder refuses a dirty theme dir. |
| Screenshot site | `wp-guide-wordpress-1`, https://wp-guide.affiliatemarketconnect.com (`--site wp-test` for the dev site) | A buyer-style install with no repo, the theme uploaded from the test zip. `affiliate-theme` active, seeded pages present, `affiliate-theme_pages_created` = 1. |
| Provider screenshots | **Pending:** `materials/setup-guides/affiliate-theme/screenshots/resend/` (empty). 1.4.1 used nine GetResponse shots (deleted in `dc169e3`). API key path: Dashboard, Tools menu, Integrations and API, API tab, Generate API key, the `-redacted` Copy API Key box. List token path: Contacts › Lists, the list's three-dot menu (1366×606), list settings. All the others were 1366×563 | Supplied by hand. The guide uses only a redacted copy of any API key shot. `.gitignore` ignores `screenshot-api-key-*resend.png` in any folder. Never commit an unredacted key shot. |
| Copy and layout | `tools/templates/setup_guide.html`, `setup_guide.css` | Edit the copy here. |

## Tools, in order

One-time setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Playwright drives the host's `/usr/bin/google-chrome` (`channel="chrome"`), so there's no `playwright install` step.

1. `.venv/bin/python tools/build_theme_zip.py` builds `deliverables/affiliate-theme.zip` from `git archive HEAD` of the theme, under an `affiliate-theme/` prefix, without `CLAUDE.md`.
2. `.venv/bin/python tools/capture_setup_screens.py [--site wp-guide|wp-test] [--only NAME ...]` writes `.tmp/setup-guide/screens/*.png` (2× scale).
   - It logs in with cookies minted by `wp eval` for user 1, and destroys the session token on exit. No password is needed.
   - It replaces what identifies the site in the DOM before each shot: the site name, the sending domain (as `yoursite.com`, with the record names Resend gives relative to the zone cut to `resend._domainkey`, `send` and `rsend`), the From name, the Reply-to, mailing and admin addresses, the affiliate URL and page statuses. Nothing is saved.
   - Shots `05b-domain` (the pending domain, records table and **Check**) and `05c-sequences` (all three Live, with the usage line) exist only at those moments: take `05b` after the settings save and before any DNS record, `05c` once the domain verifies.
   - Shot 04 (Settings › Permalinks) replaces the dev site's address with `https://yoursite.com` in the structure examples and the Optional help text.
   - With `--site wp-test` only: loading Settings › Permalinks runs core's `flush_rewrite_rules()`, which rewrites wp-test's repo-root `.htaccess`. With the dev site on `/%postname%/` the file comes out unchanged. Check `git -C /home/tevis/wp-test status` after a capture anyway. wp-guide's install lives in a Docker volume, outside any repo.
   - Shots 01–03 switch the dev site to `twentytwentyfive` and back. The tool checks the seed flag first, then checks that the stylesheet and the page list are unchanged. If it ever reports "site not restored", run `wp theme activate affiliate-theme` and compare `wp post list --post_type=page`.
3. **Redact the API key shot.** For 1.4.1 this was done once, and the `-redacted` copy was committed. The command below is that GetResponse run, kept as the pattern. Its folder no longer exists, and a Resend key shot needs its own boxes. A hand-drawn scribble is not enough: the first supplied shot still showed the key's first 8 characters and GetResponse's masked `lb9…yl6` row. Paint over the whole key field and the masked row of the new unredacted shot, then view the result before building:

   ```bash
   G=materials/setup-guides/affiliate-theme/screen-shots/getresponse; IN=$G/screen-shot-api-key-email-marketing-software-getresponse.png
   .venv/bin/python tools/redact_image.py "$IN" .tmp/setup-guide/gr/step1.png --fill '#ffffff' --box '436,299,414,38:••••••••••••••••••••••••••••••••'
   .venv/bin/python tools/redact_image.py .tmp/setup-guide/gr/step1.png "${IN%.png}-redacted.png" --box 60,369,112,22
   ```

   The box coordinates fit the 1366×563 shot supplied on 2026-09-27. A new screenshot needs new boxes. The second box's fill is sampled from the pixel to its left, so it matches the dimmed background.
4. `.venv/bin/python tools/mark_getresponse_shots.py` crops the GetResponse shots and draws the same red boxes and badges as the WordPress shots, into `.tmp/setup-guide/screens/gr-*.png`. The crops and marks are measured in source pixels on the 2026-09-28 shots. The tool stops on any shot that isn't the size it was measured on (1366×563; the three-dot menu shot is 1366×606, set in `SIZES`), and a replaced shot of the same size still needs its numbers checked. The list-token mark has no badge on purpose: a badge there covers the start of "List token:". **Its `SRC` folder was deleted in `dc169e3`, so the tool fails until it is pointed at the Resend shots (see Status).**
5. `.venv/bin/python tools/build_setup_guide.py [--draft]` writes `deliverables/SETUP-GUIDE.pdf`. It fails on any missing image. `--draft` only lets the GetResponse screen-shots be missing, and stamps DRAFT on every page.

## Verification (all must pass before publishing)

1. **Zip:** `unzip -l deliverables/affiliate-theme.zip` shows `affiliate-theme/style.css` one level down and no `CLAUDE.md`. The file list equals `git ls-tree -r --name-only HEAD:wp-content/themes/affiliate-theme` minus CLAUDE.md, and `php -l` passes on every PHP file extracted to `.tmp/`. `zipinfo deliverables/affiliate-theme.zip` shows `drwxr-xr-x` on every folder and `-rw-r--r--` on every file. Mode `?---------` or `?rw-------` means the builder copied git archive's empty MS-DOS attributes again; buyers who unzip that on a Mac get folders they can't open.
2. **Screens:** open every PNG, including the `gr-*` crops and a 150-dpi render of the PDF page holding the GetResponse click path (page 8). Check that no character of the API key shows. In the WordPress shots, check for no real list token, list name, affiliate URL or site name. (The GetResponse list-token shot shows the real token on purpose: a token is not a credential without the key.) Also check that no modal or admin notice covers a marked control.
3. **Labels:** every UI string the guide quotes is grepped against the theme source or WordPress core. Any `MISSING` means the guide is wrong. Add a row whenever the guide quotes a new string, and remove a row when the guide stops quoting it. `A static page` is not in this list: core wraps "static page" in a link, so check it against the Reading screen-shot instead. GetResponse's labels (`Tools`, `Connect`, `Integrations and API`, `API`, `Generate API key`, `Generate`, `Copy`, `Contacts`, `Lists`, `Settings`, `List token:`, `List name`, `List ID`) can't be grepped, so check them against the supplied shots. GetResponse now says "Integrations and API", and since theme 1.2.6 the theme's settings screen and its rejected-key message do too. **Against theme 1.5.0, nine rows print `MISSING`:** the three GetResponse field and status labels, `Check list`, the three GetResponse error messages, and the sign-up handler's `Something went wrong. Please try again.` and `Please try again in a moment.`. That is expected: 1.5.0 removed them, and the guide is wrong until Step 5 is rewritten for Resend.

   ```bash
   T=/home/tevis/wp-test/wp-content/themes/affiliate-theme; W=/home/tevis/wp-test
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
- **The zip must stay under 2 MB (2,097,152 bytes).** That is PHP's default `upload_max_filesize`, which WordPress uses as its upload limit, so a bigger zip won't install on a host left at the defaults. The troubleshooting entry for "The link you followed has expired." also says "under 2 MB". Check `stat -c %s deliverables/affiliate-theme.zip` on every rebuild. Theme 1.4.1 grew the zip from 1.15 MB to 1,721,299 bytes, almost all of it `emails/landing-3/guide.pdf`, which leaves about 370 KB of headroom. 1.5.0 deleted `emails/`, guide included. If the Resend work puts the guide back in the theme, the headroom becomes a constraint again.
- **Selecting a Permalinks radio fills the Custom Structure box** (`wp-admin/js/common.js`), so Post name shows `/%postname%/` there. The guide quotes that.
