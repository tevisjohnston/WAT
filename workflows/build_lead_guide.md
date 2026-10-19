# Build the landing-3 guide.pdf (The Lead-First Affiliate Guide)

## Objective

Produce `guide.pdf`, the guide that the wp-test affiliate theme's Long Form landing page promises ("The guide arrives in the next few minutes").

The guide is written for the buyer's subscribers, who are aspiring affiliates, not for the buyer. It names no brand, no author and no offer: every buyer sends the same file under their own name. Its five chapter titles are the five "What Is In The Guide" bullets of `Affiliate_Theme_Theme_landing_pattern_long()`, word for word. Chapter 3's seven email templates follow the seven-step shape of the old landing-3 email sequence (Deliver, Teach, Help, Show the plan, Clear the obstacle, Give a tool, Invite).

## Status: no delivery path until the Resend work lands

Up to theme 1.4.1, the PDF lived at `affiliate-theme/emails/landing-3/guide.pdf`. The theme packed it next to `index.html` in the ZIP of landing-3's first email, and the buyer uploaded that ZIP to GetResponse. Theme 1.5.0 (wp-dfy `d62daf2`) deleted `emails/`, guide and email sequences included, ahead of the move to Resend. The Long Form pattern still promises the guide. Where the guide lives, and how subscribers receive it, will be decided when Resend lands. The old emails are in wp-test history (`git show 728e991:wp-content/themes/affiliate-theme/emails/...`).

Until then:

- **Run the tool only with `--no-copy`.** A plain run builds the PDF and then crashes on the copy, because `emails/landing-3/` no longer exists and the tool does not create it. Don't recreate the folder by hand either: that would put back a path 1.5.0 removed.
- Steps 2 and 3–4 of the verification below describe the 1.4.1 delivery and are suspended.
- When the delivery path is decided, point `THEME_PDF` in `tools/build_lead_guide.py` at it (or drop the copy step), and rewrite this Objective, step 2, and verification steps 3–4 to match.

## When to rebuild

- The guide copy or layout changes (`tools/templates/lead_guide.html`, `lead_guide.css`).
- The Long Form pattern's "What Is In The Guide" list changes. The build fails until the chapter titles match it again. Once Resend brings back an email sequence that cites the chapters by number (the 1.4.1 landing-3 emails 1–7 did), check those too.
- The theme's Archivo or Newsreader font files change.

A theme `Version` bump alone does not need a rebuild: the guide prints no version.

## Inputs

| Input | Where | Notes |
|---|---|---|
| Copy and layout | `tools/templates/lead_guide.html`, `lead_guide.css` | Edit the copy here. Same palette and fonts as `setup_guide.css`. |
| Theme fonts | `/home/tevis/wp-test/wp-content/themes/affiliate-theme/assets/fonts/` | Read in place through `{{FONTS}}`. |
| The landing promise | `inc/affiliate-theme-funnel.php`, `Affiliate_Theme_Theme_landing_pattern_long()` | The tool reads its `<li>` items under "What Is In The Guide". |

## Tools, in order

One-time setup as in `build_setup_guide.md`: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Playwright drives `/usr/bin/google-chrome`.

1. `.venv/bin/python tools/build_lead_guide.py [--no-copy]` does the following:
   - fills `{{CSS}}` and `{{FONTS}}`
   - checks that every landing bullet appears in the guide
   - prints `.tmp/lead-guide/guide.pdf` and checks that both theme fonts loaded
   - fails over 2 MB (the cap that kept `affiliate-theme.zip` under PHP's upload limit while the guide shipped inside it)
   - copies the PDF into the theme's `emails/landing-3/`, which **crashes against theme 1.5.0** (see Status)

   `--no-copy` builds into `.tmp/lead-guide/` only. This is the only mode that works today.
2. **Suspended (1.4.1 delivery).** Commit the PDF in wp-test, using the theme's commit message style and a `Version` bump. Then follow `build_setup_guide.md` from its step 1 to rebuild `affiliate-theme.zip`.

## Verification (all must pass before committing)

1. **PDF:** `pdfinfo` shows Letter and 15 pages. Expect a different page count after copy changes. `pdffonts` lists Archivo and Newsreader as embedded.
2. **Pages:** `pdftoppm -r 55 -png` every page, tile them with `montage`, and review them. Look for widowed headings, a short list split across a page break (give it `class="keep"`), clipped wireframe badges, and overflow. Each chapter starts on a new page, so a short last page at the end of a chapter is expected.
3. **Suspended (1.4.1 delivery).** The emails that ship it: build landing 3's download on the dev site. Confirm that `01-your-guide.zip` holds `index.html` and a `guide.pdf` byte-identical to the theme's. 1.5.0 removed the download, so replace this check with whatever Resend delivery replaces it.
4. **Suspended (1.4.1 delivery).** GetResponse: after the upload, the guide button in landing-3 email 1's preview opens the PDF. This was never checked before GetResponse was removed.

## Known quirks

- **Chrome clips anything that crosses into the page margin.** The chapter 2 wireframe starts at the left margin, so its number badges sit inside its wide left padding. Badges positioned outside it were cut in half.
- **Chrome embeds the variable fonts as Type 3**, as with the setup guide, which is why the PDF is about 800 KB for text alone. Poppler's "Bad bounding box in Type 3 glyph" warnings are harmless.
- **It was never confirmed whether GetResponse hosted a PDF from an uploaded ZIP.** Theme 1.4.1 hedged by telling buyers to upload the guide to their Media Library and relink it. Self-hosting from the buyer's Media Library is the starting point to consider for Resend.
