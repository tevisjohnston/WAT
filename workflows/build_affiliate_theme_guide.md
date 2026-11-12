# Build the Affiliate Theme Guide (affiliate-theme-guide.pdf)

## Objective

Produce the buyer-facing `affiliate-theme-guide.pdf` and the `affiliate-theme.zip` it tells buyers to upload, then publish both to Affiliate Market Connect's secure downloads. The guide covers the buyer path at the top of `/home/tevis/wp-test/wp-content/themes/affiliate-theme/CLAUDE.md`, and only that path:

download → upload → install → activate → Settings › Permalinks (Post name) → Settings › Affiliate Theme Settings (the Resend API key, the sending domain, the sender details, the mailing address, the affiliate URL) → save (the theme adds the domain and sets up the emails) → add the DNS records → **Check** → edit and publish a landing page → Settings › Reading → edit and publish the legal pages → Settings › Privacy.

The Permalinks step (guide Step 4) was added on 2026-09-28 so buyers' pages get readable addresses before anything is published. Theme 2.0.0 put Resend in place of GetResponse: the guide's Steps 5–7 (the Resend account and key, the settings, the DNS records) and its "Your email sequences" page are new.

It does not cover VPS or Docker deployment. DNS is covered only as far as adding Resend's records. The stale `dfy-wordpress-website.zip` (theme v1.1.0) is a separate deliverable.

## When to rebuild

**`deliverables/` holds theme 2.0.0 since 2026-11-06, built but not published**: members still download 1.4.1 until the owner says to publish. Rebuild into `deliverables/` on the triggers below. A zip for testing on wp-guide still goes to `.tmp/wp-guide/affiliate-theme.zip` (`build_theme_zip.py --out`), and a guide with missing shots is built with `--draft --out .tmp/affiliate-theme-guide/affiliate-theme-guide-draft.pdf`.

- The theme's `Version` in `style.css` changes. The cover prints it, and the zip must match it.
- Any settings-screen label, help text, status or error string that the guide quotes changes (`inc/affiliate-theme-funnel.php`, `inc/affiliate-theme-resend.php`, `inc/affiliate-theme-legal.php`, `assets/js/admin-settings.js`, `blocks/optin-form/`).
- The buyer path in the theme's CLAUDE.md changes.
- A WordPress core update renames a screen or button that the guide quotes (for example, 7.1 says **Add Theme**, not "Add New Theme").
- A Resend or Cloudflare dashboard screen or button that the guide quotes or shows changes. Retake the shot, then re-measure its `SHOTS` entry.

## Inputs

| Input | Where | Notes |
|---|---|---|
| Theme source | `/home/tevis/wp-test` at `HEAD` | Must be committed. The zip builder refuses a dirty theme dir. |
| Screenshot site | `wp-guide-wordpress-1`, https://wp-guide.affiliatemarketconnect.com (`--site wp-test` for the dev site) | A buyer-style install on the Free Resend account, with no repo. The theme is uploaded from the test zip. `affiliate-theme` active, seeded pages present, `affiliate-theme_pages_created` = 1, the domain verified and all three sequences Live. |
| Provider screenshots | `materials/guides/affiliate-theme/screenshots/resend/` and `cloudflare/` | Taken by the owner in Firefox on the Free account (wp-guide) and in Cloudflare, except three: `resend/screenshot-21-*` comes from the Pro account, and `screenshot-31-*` and `-32-*` from a Free account with no domain. Numbered in the file name, at mixed window widths (1319–1366). `mark_resend_shots.py` holds each one's size. The guide reads only the `-redacted` copies of the API key list shots (3 and 6). `.gitignore` ignores `screenshot-api-key-*resend.png` in any folder. Never commit an unredacted key shot. 1.4.1's nine GetResponse shots are in git history only (`git show 1ec2bd4:materials/guides/affiliate-theme/screen-shots/getresponse/<file>`). |
| Owner's settings copy | `materials/guides/affiliate-theme/affiliate-theme-settings-copy/affiliate-theme-settings-copy.md` | Source text only. It was written against an older settings screen ("Verify DNS records", "Update these emails", "one a day"), so check every string against 2.0.0 before using it. |
| Copy and layout | `tools/templates/affiliate_theme_guide.html`, `affiliate_theme_guide.css` | Edit the copy here. |

## Tools, in order

One-time setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Playwright drives the host's `/usr/bin/google-chrome` (`channel="chrome"`), so there's no `playwright install` step.

1. `.venv/bin/python tools/build_theme_zip.py [--out PATH]` builds `deliverables/affiliate-theme.zip` (or `PATH`; the wp-guide test zip is `--out .tmp/wp-guide/affiliate-theme.zip`) from `git archive HEAD` of the theme, under an `affiliate-theme/` prefix, without `CLAUDE.md`.
2. `.venv/bin/python tools/capture_setup_screens.py [--site wp-guide|wp-test] [--only NAME ...]` writes `.tmp/affiliate-theme-guide/screens/*.png` (2× scale).
   - It logs in with cookies minted by `wp eval` for user 1, and destroys the session token on exit. No password is needed.
   - It replaces what identifies the site in the DOM before each shot: the site name, the sending domain (as `yoursite.com`, with the record names Resend gives relative to the zone cut to `resend._domainkey`, `send`, `rsend` and `links`; the cut keys off the stored sending domain too when it differs from the site's host), the key mask's last four characters, the From line, the Reply-to, mailing and admin addresses, the affiliate URL and page statuses. It hides the admin bar's Gravatar, which can be a real photo. Nothing is saved.
   - Shots `05b-domain` (the pending domain, records table and **Check**) and `05c-sequences` (all three Live) exist only at those moments: take `05b` after the settings save and before any DNS record, and `05c` once the domain verifies. wp-guide's domain is verified, so it shows no records table or **Check**. The current `05b` was retaken on 2026-11-11 with `--site wp-test` against the skill's fake Resend API, so no real account was touched: save the theme's options (`affiliate-theme_settings`, `affiliate-theme_resend`, and `affiliate-theme_fake_resend` and the lock row, absent then), put a temporary `wp-content/mu-plugins/0-capture-fake.php` that defines `AFFILIATE_THEME_FAKE_RESEND` (it must sort before `affiliate-theme-dev.php`), set the Sending domain to `wp-track.affiliatemarketconnect.com` and run `Affiliate_Theme_Theme_domain_step()` with WP-CLI (the fake makes the domain pending with its five records), capture `--only 05b-domain` (badges: 1 the records table, 2 the **Open yoursite.com in Resend** link, given an 18px left margin in the capture so its badge clears the sentence before it, 3 **Check**, matching Step 7's list), then delete the mu-plugin, write the saved options back (delete the absent ones), call `Affiliate_Theme_Theme_flush_cache()`, and compare the options' hashes with the saved ones.
   - `07-editor-publish` marks the form (1), the **Sequence** select (2) and **Publish** (3). `06` and `09` put the badge left of the link so "— draft" stays readable.
   - Shot 04 (Settings › Permalinks) replaces the site's address with `https://yoursite.com` in the structure examples and the Optional help text.
   - With `--site wp-test` only: loading Settings › Permalinks runs core's `flush_rewrite_rules()`, which rewrites wp-test's repo-root `.htaccess`. With the dev site on `/%postname%/` the file comes out unchanged. Check `git -C /home/tevis/wp-test status` after a capture anyway. wp-guide's install lives in a Docker volume, outside any repo.
   - Shots 01–03 switch the site to `twentytwentyfive` and back. The tool checks the seed flag first, then checks that the stylesheet and the page list are unchanged. If it ever reports "site not restored", run `wp theme activate affiliate-theme` and compare `wp post list --post_type=page`.
3. **Redact the API key list shots.** Resend's API Keys list shows each key's first characters in its Token column, so shots 3 and 6 were redacted once with `tools/redact_image.py` into `-redacted.png` copies, which are the only ones committed and read. A new key shot needs its own boxes, measured on that file. Paint over the whole Token cell of every row, and any key shown in full, then view the result before building:

   ```bash
   R=materials/guides/affiliate-theme/screenshots/resend; IN=$R/<shot>.png
   .venv/bin/python tools/redact_image.py "$IN" "${IN%.png}-redacted.png" --box x,y,w,h [--box ...] [--fill '#rrggbb']
   ```

   A hand-drawn scribble is not enough: 1.4.1's first GetResponse shot still showed the key's first 8 characters after one. Without `--fill`, a box's fill is sampled from the pixel to its left, so it matches the background. Shot 5 (the new key, shown once) shows the key as dots and needs no redaction.
4. `.venv/bin/python tools/mark_resend_shots.py` crops the Resend and Cloudflare shots and draws the same red boxes and badges as the WordPress shots (it imports `MARK_JS` from the capture tool), into `.tmp/affiliate-theme-guide/screens/rs-1`…`rs-15` and `cf-2`, `cf-4` and `cf-5`. It also crops `amc-1-download` for Step 1 from `affiliate-market-connect/screenshot-1-amc.png` (1308×2125, the members page `affiliatemarketconnect.com/members/domain-web-hosting`, added 2026-11-11): the **Downloadable Resources** card with the **Download DFY WordPress Website (.zip)** row marked 1. It shows no test domain, so it needs no `PAINT`. `rs-1`…`rs-4` are Step 5's key, `rs-5`…`rs-9`, `cf-2` and `cf-4` are Step 7's domain, records and Cloudflare (badges 1–6 follow Step 7's Cloudflare list: `cf-2` **Add record**, and `cf-4`, a CNAME, the Type, Name, Target, Proxy status and TTL, and Save; the owner dropped the TXT shot `cf-3` on 2026-11-10 as redundant with `cf-4`, and the account-home and **DNS Records** shots `cf-1` and `cf-1-2` on 2026-11-11, since the list's **Go to** line already names the DNS Records page; their sources stay in `materials/`). `rs-10`…`rs-13` are Step 7's "If your domain was already in Resend" box, and `rs-14` (the **Enable receiving** switch) and `rs-15` (the receiving MX row) are Step 7's "Optional: read replies in Resend". The switch sits right of the Status column, so `rs-14` shows only the heading row and `rs-15` the MX row without its Status. Every crop and mark is in source pixels, measured on the shots supplied 2026-10-25 to 2026-10-30, and each `SHOTS` entry holds its source's size: the tool stops on any shot of another size, and a replaced shot of the same size still needs its numbers checked. Every crop leaves out the account switcher (the Resend team name, the Cloudflare login) and the records tables' Status column. Before cropping, the tool's `PAINT` step replaces the owner's test domain with `yoursite.com`, the apex most buyers use and the name the WordPress shots show (owner, 2026-11-06): it paints the `.wp-guide` ending off record names (`send.wp-guide` → `send`, the receiving MX's `wp-guide` → `@`) and writes `yoursite.com` over full names in Inter (`materials/fonts/inter/`, OFL), sized to the old word's ink box. The boxes were found with `tesseract <shot> - --psm 11 tsv`; after any change, run tesseract over every finished `rs-*` and `cf-*` crop and grep for `wp-guide`, `affiliatemarket` and the account names, which must print nothing. The marks on the **Verified** and **Partially Verified** pills and on **I've added the record** have no badge on purpose.
5. `.venv/bin/python tools/build_affiliate_theme_guide.py [--draft] [--out PATH]` writes `deliverables/affiliate-theme-guide.pdf`. It fails on any missing image. `--draft` lets only the hand-supplied shots (`data-rs` in the template) be missing, and stamps DRAFT on every page.

## Verification (all must pass before publishing)

1. **Zip:** `unzip -l deliverables/affiliate-theme.zip` shows `affiliate-theme/style.css` one level down and no `CLAUDE.md`. The file list equals `git ls-tree -r --name-only HEAD:wp-content/themes/affiliate-theme` minus CLAUDE.md, and `php -l` passes on every PHP file extracted to `.tmp/`. `zipinfo deliverables/affiliate-theme.zip` shows `drwxr-xr-x` on every folder and `-rw-r--r--` on every file. Mode `?---------` or `?rw-------` means the builder copied git archive's empty MS-DOS attributes again; buyers who unzip that on a Mac get folders they can't open.
2. **Screens:** open every PNG, including the `rs-*` and `cf-*` crops, and a 150-dpi render of the PDF pages holding Steps 5 and 7. Check that no character of an API key shows, and no Resend team or account name, Cloudflare login or `wp-guide` name. In the WordPress shots, check for no real sending domain, From line, mailing address, Reply-to, affiliate URL or site name. Also check that no modal or admin notice covers a marked control.
3. **Labels:** every UI string the guide quotes is grepped against the theme source or WordPress core. Any `MISSING` means the guide is wrong, and against wp-test `HEAD` the grep prints nothing. Add a row whenever the guide quotes a new string, and remove a row when the guide stops quoting it. The guide's disguised `yoursite.com` is the theme's `%s`, and a string the theme assembles is grepped by its fixed part. The theme writes the status names in lower case and the screen capitalizes them, so they are a second, case-insensitive list.

   ```bash
   T=/home/tevis/wp-test/wp-content/themes/affiliate-theme; W=/home/tevis/wp-test
   check() { while IFS='|' read -r label where; do where=$(eval echo "$where")
     grep -rq$1F -- "$label" $where || echo "MISSING $label"; done; }
   check '' <<'EOF'
   Affiliate Theme Settings|$T/inc
   Full access|$T/inc
   Sending access|$T/inc
   Sender|$T/inc
   Funnel|$T/inc
   Affiliate link|$T/inc
   Success message|$T/inc
   Resend accepted this key.|$T/inc
   Resend did not accept this key.|$T/inc
   That is not a Resend API key. A Resend API key starts with re_.|$T/inc
   This key can only send email. The theme needs a key with Full access.|$T/inc
   WordPress could not reach Resend. Reload this page in a minute.|$T/inc
   The affiliate link is not a usable address. Start it with https://.|$T/inc
   Your sending domain|$T/inc
   The theme added <strong>%s</strong> to your Resend account. Add the DNS records below.|$T/inc
   %s is verified.|$T/inc
   Open %s in Resend|$T/inc
   is waiting for its DNS records.|$T/inc
   Full host name|$T/inc
   tracking is off for this domain.|$T/inc
   already in use in another Resend account|$T/inc
   Your email sequences|$T/inc
   Setting up your emails in Resend|$T/assets/js
   'Step ' + (|$T/assets/js
   Waiting for: |$T/inc
   a verified sending domain|$T/inc
   your mailing address|$T/inc
   a usable affiliate link|$T/inc
   in Resend that %s not published. Publish or discard %s there, then save these settings.|$T/inc
   It was turned off in Resend.|$T/inc
   The theme has newer copy for these emails. Reset to use it.|$T/inc
   Finish setting up emails|$T/inc
   Turn off|$T/inc
   Turn on|$T/inc
   Open in Resend|$T/inc
   Reset these emails to the theme's copy|$T/inc
   Replace my edits in Resend|$T/inc
   Your landing pages|$T/inc
   Your legal pages|$T/inc
   Opt-in form is not ready:|$T/blocks
   add your Resend API key|$T/inc
   the %s emails are turned off|$T/inc
   the %s emails wait for %s|$T/inc
   the %s emails are not set up in Resend yet|$T/inc
   are not turned on yet|$T/inc
   Sign-ups here start the|$T/blocks
   Sequence|$T/blocks
   This page's emails|$T/blocks
   Button text|$T/blocks
   Email field label|$T/blocks
   Ask for a first name|$T/blocks
   Name field label|$T/blocks
   Please try again in a moment.|$T/inc
   Please try again in a few minutes.|$T/inc
   Service unavailable. Please try again shortly.|$T/inc
   Something went wrong. Please try again.|$T/inc
   Legal — Privacy: Analytics and Advertising|$T/patterns
   — All rights reserved.|$T/parts
   Theme installed successfully.|$W/wp-admin/includes
   The theme is missing the %s stylesheet.|$W/wp-admin/includes
   The link you followed has expired.|$W/wp-includes
   This theme is already installed.|$W/wp-admin/includes
   Replace installed with uploaded|$W/wp-admin/includes
   Add Theme|$W/wp-admin
   Upload Theme|$W/wp-admin
   Install Now|$W/wp-admin
   Permalink structure|$W/wp-admin/options-permalink.php
   Post name|$W/wp-admin/options-permalink.php
   Custom Structure|$W/wp-admin/options-permalink.php
   Save Changes|$W/wp-admin
   Your homepage displays|$W/wp-admin/options-reading.php
   Change your Privacy Policy page|$W/wp-admin
   Use This Page|$W/wp-admin
   Are you ready to publish?|$W/wp-includes/js/dist
   Set featured image|$W/wp-includes
   Add an excerpt|$W/wp-includes/js/dist
   EOF
   check i <<'EOF'
   Live|$T/inc/affiliate-theme-resend.php
   Waiting|$T/inc/affiliate-theme-resend.php
   Needs update|$T/inc/affiliate-theme-resend.php
   Not set up|$T/inc/affiliate-theme-resend.php
   Setting up|$T/inc/affiliate-theme-resend.php
   Off|$T/inc/affiliate-theme-resend.php
   EOF
   ```

   The seven placeholders must be spelled exactly as they are in `inc/affiliate-theme-legal.php`. Some quoted strings can't be grepped, so check them against the screenshots instead: `A static page` (core wraps "static page" in a link; the Reading shot); Resend's `API keys`, `Type`, `Name`, `Content`, `TTL`, `Priority`, `Proxy status`, `DNS Only`, `Create API key`, `Permission`, `Full access`, `Sending access`, `Add`, `Done`, `Domains`, `All domains`, `Records`, `Domain Verification`, `Enable Sending`, `Enable Tracking`, `Enable receiving`, `Inboxes`, `Emails`, `Receiving`, `Configuration`, `Enable tracking metrics`, `Configure`, `Subdomain`, `Enable open tracking`, `Enable click tracking`, `Auto configure`, `I've added the record`, `Verified`, `Partially Verified`, `Onboarding`, `Metrics`, `Templates` and `Automations`; Cloudflare's `DNS`, `Records`, `Add record`, `Type`, `Name`, `Target`, `Mail server`, `Priority`, `Proxy status`, `DNS only` and `Save`. The browser's `Choose File` and macOS's `Compress "affiliate-theme"` are checked against the browser and Finder.
4. **PDF:** `pdfinfo` (Letter), `pdffonts` (Archivo and Newsreader embedded), then `pdftoppm -r 90` and review every page for widowed headings, stranded figures, a red badge sliced across a page break, and overflow.

## Publish

```bash
D=/home/tevis/affiliatemarketconnect.com/wp-content/uploads/amc-secure-assets
install -m 0644 -o root -g root deliverables/affiliate-theme-guide.pdf deliverables/affiliate-theme.zip "$D"/
docker exec affiliatemarketconnectcom-wordpress-1 test -r /var/www/html/wp-content/uploads/amc-secure-assets/affiliate-theme-guide.pdf && echo readable
```

Members download them through `/wp-json/amc/v1/download?file=affiliate-theme-guide.pdf` and `?file=affiliate-theme.zip`. The download buttons on the Domain + Web Hosting step are added by hand in the affiliate-market-connect theme. This workflow doesn't touch that theme. Those files are tracked in the affiliatemarketconnect.com repo, so commit there only when asked.

The guide was named `SETUP-GUIDE.pdf` until 2026-11-08, and 1.4.1's copy still sits in `amc-secure-assets/` under that name. On the first 2.0.0 publish, remove that old file and point any download button that uses `?file=SETUP-GUIDE.pdf` to `?file=affiliate-theme-guide.pdf`, or members get the old guide.

## Known quirks

- **The block editor never goes network-idle** because of heartbeat polling. Wait on `wp.data` state, not on `networkidle`.
- **WP-CLI `post list --name=`** does not find draft pages. Use `get_page_by_path()` in `wp eval`.
- **The Reading screen's Homepage dropdown lists only published pages.** That is why the guide publishes the landing page (Step 8) before Settings › Reading (Step 9).
- **A native `<select>` popup can't be screen-shotted.** The privacy shot redraws the list as a list box (`size = options.length`). In a buyer's dropdown, the "checkmark" is the currently selected entry, which is WordPress's own draft (ID 3 on the dev site).
- **Settings › Privacy's link text depends on the page's status.** It reads "Edit or **view**" for a published page and "Edit or **preview**" for a draft (`options-privacy.php`). The guide uses this as its "did you pick the right one" check.
- **A Site Editor save shadows the theme's template files.** If a template or part looks wrong in a shot, check `wp post list --post_type=wp_template_part` for an override.
- **Chrome embeds the variable fonts as Type 3.** Poppler prints "Bad bounding box in Type 3 glyph" warnings. They're harmless, and the text renders and extracts correctly.
- **The theme's `screenshot.png` (1200×900) arrived in wp-dfy commit `63c1940` (on GitHub only).** Its card on the Themes screen (shot 03) shows the landing page. An older zip without it shows a blank checkerboard.
- **Step 6 fills page 9** (measured 2026-11-10): page 9 holds Step 6's whole list, through "Click Save Changes.", and page 10 starts with the "What happens when you save" box. A copy edit in Steps 5 or 6 can push the list across the break and slice a red badge in two, so after one check that `pdftotext -f 9 -l 9` still holds "Click Save Changes." or ends on a whole item. Step 8's list ends on page 18 only since `07-editor-publish` went from `w88` to `w80` (2026-11-10): at `w88`, "Click Publish." fell alone onto page 19.
- **A host Python upgrade breaks `.venv`.** Its `python3` symlinks to `/usr/bin/python3`, so when that moved from 3.12 to 3.14 (found 2026-10-02) the packages in `lib/python3.12/` vanished and the capture tool failed with `No module named 'playwright'`. Rebuild it: `rm -rf .venv` then rerun the one-time setup.
- **The zip must stay under 2 MB (2,097,152 bytes).** That is PHP's default `upload_max_filesize`, which WordPress uses as its upload limit, so a bigger zip won't install on a host left at the defaults. The troubleshooting entry for "The link you followed has expired." also says "under 2 MB". Check `stat -c %s` on every rebuild. Theme 1.4.1's zip was 1,721,299 bytes. The 2.0.0 test zip (`.tmp/wp-guide/affiliate-theme.zip`, built at `ebf5ef6`) is 1,753,639 bytes, about 343 KB of headroom, and most of it is the Long Form guide, `assets/lead-magnets/landing-3-guide.pdf` (`workflows/build_lead_guide.md`).
- **The theme writes its sequence statuses in lower case** (`'needs update'`, `'not set up'`) and the screen capitalizes them, which is why the label grep has a case-insensitive list.
- **Resend offers Auto configure for Cloudflare at its own discretion.** It was missing for weeks, then came back for the tracking CNAME (2026-10-30), so the guide calls it optional and always gives the by-hand way.
- **Selecting a Permalinks radio fills the Custom Structure box** (`wp-admin/js/common.js`), so Post name shows `/%postname%/` there. The guide quotes that.
