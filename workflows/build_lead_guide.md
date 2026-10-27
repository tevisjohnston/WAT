# Build the landing-3 guide.pdf (The Lead-First Affiliate Guide)

## Objective

Produce `guide.pdf`, the guide that the wp-test affiliate theme's Long Form landing page promises ("The guide arrives in the next few minutes"). From theme 2.0.0 the theme serves it as `assets/lead-magnets/landing-3-guide.pdf`, and Long Form email 1 links it through the `{{{GUIDE_URL}}}` template variable.

The guide is written for the buyer's subscribers, who are aspiring affiliates, not for the buyer. It names no brand, no author and no offer: every buyer sends the same file under their own name. Its five chapter titles are the five "What Is In The Guide" bullets of `Affiliate_Theme_Theme_landing_pattern_long()`, word for word. Chapter 3's seven email templates follow the seven-step shape of the old landing-3 email sequence (Deliver, Teach, Help, Show the plan, Clear the obstacle, Give a tool, Invite). Theme 2.0.0's Long Form email 4 maps its six emails onto that shape.

## Status: the guide ships in theme 2.0.0

Up to theme 1.4.1, the PDF lived at `affiliate-theme/emails/landing-3/guide.pdf`, packed into the ZIP of landing-3's first email for GetResponse. Theme 1.5.0 (wp-dfy `d62daf2`, on GitHub only) deleted `emails/`, guide and email sequences included, ahead of the move to Resend. Theme 2.0.0, built on wp-test branch `resend-2.0.0` and on `main` since that branch merged on 2026-10-25, brings the guide back at `affiliate-theme/assets/lead-magnets/landing-3-guide.pdf`. The theme's Resend templates link it from Long Form email 1: the `{{{GUIDE_URL}}}` variable's fallback is the PDF's URL on the buyer's own site.

- The tool copies the PDF there and creates the folder. Run it while wp-test has `main` checked out (2.0.0 since 2026-10-25; 1.5.0 had no `assets/lead-magnets/`).
- Don't rebuild `affiliate-theme.zip` because the guide changed. `build_setup_guide.md` says when a rebuild is allowed.

## When to rebuild

- The guide copy or layout changes (`tools/templates/lead_guide.html`, `lead_guide.css`).
- The Long Form pattern's "What Is In The Guide" list changes. The build fails until the chapter titles match it again. Long Form's emails cite the chapters too (theme `emails/landing-3/`: email 1 lists all five, and emails 2–6 take one chapter each), so change them to match.
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
   - fails over 2 MB (`affiliate-theme.zip` holds the guide again from 2.0.0, and must stay under PHP's 2 MB upload limit)
   - copies the PDF to the theme's `assets/lead-magnets/landing-3-guide.pdf`, creating the folder

   `--no-copy` builds into `.tmp/lead-guide/` only.
2. Commit the PDF in wp-test, using the theme's commit message style and a `Version` bump (until 2.0.0 is released, `Version` stays 2.0.0). Then follow `build_setup_guide.md` from its step 1 to rebuild `affiliate-theme.zip`, once that workflow allows a rebuild.

## Verification (all must pass before committing)

1. **PDF:** `pdfinfo` shows Letter and 15 pages. Expect a different page count after copy changes. `pdffonts` lists Archivo and Newsreader as embedded.
2. **Pages:** `pdftoppm -r 55 -png` every page, tile them with `montage`, and review them. Look for widowed headings, a short list split across a page break (give it `class="keep"`), clipped wireframe badges, and overflow. Each chapter starts on a new page, so a short last page at the end of a chapter is expected.
3. **The link:** the dev site serves the PDF. `curl -sI https://wp-test.affiliatemarketconnect.com/wp-content/themes/affiliate-theme/assets/lead-magnets/landing-3-guide.pdf` shows `200` and `content-type: application/pdf`.
4. **Live:** the guide button in a real Long Form email 1 opens the PDF. This waits for the theme's live Resend test (Phase 7 of its build plan).

## Known quirks

- **Chrome clips anything that crosses into the page margin.** The chapter 2 wireframe starts at the left margin, so its number badges sit inside its wide left padding. Badges positioned outside it were cut in half.
- **Chrome embeds the variable fonts as Type 3**, as with the setup guide, which is why the PDF is about 800 KB for text alone. Poppler's "Bad bounding box in Type 3 glyph" warnings are harmless.
- **The PDF is public.** Anyone can fetch it from the theme folder without signing up, which is fine for a free guide. A security plugin that blocks direct access to theme folders breaks the link, and a renamed theme folder changes its URL.
