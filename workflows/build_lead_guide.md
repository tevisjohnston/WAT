# Build the landing-3 guide.pdf (The Lead-First Affiliate Guide)

## Objective

Produce `guide.pdf`, the guide that the wp-dfy affiliate theme's Long Form landing page promises ("The guide arrives in the next few minutes"). It goes into the theme at `/home/tevis/wp-dfy/wp-content/themes/affiliate-theme/emails/landing-3/guide.pdf`. The theme puts it next to `index.html` in the ZIP of landing-3's first email, which the buyer uploads to GetResponse. So the PDF reaches buyers only through a wp-dfy commit and the next `affiliate-theme.zip`.

The guide is written for the buyer's subscribers, who are aspiring affiliates, not for the buyer. It names no brand, no author and no offer: every buyer sends the same file under their own name. Its five chapter titles are the five "What Is In The Guide" bullets of `Affiliate_Theme_Theme_landing_pattern_long()`, word for word. Chapter 3's seven email templates follow the same seven-step shape as the landing-3 email sequence (Deliver, Teach, Help, Show the plan, Clear the obstacle, Give a tool, Invite), and landing-3 email 4 walks through it.

The emails themselves, and the theme code that builds them into ZIPs, live in the theme: see **Email sequences** in the theme's CLAUDE.md.

## When to rebuild

- The guide copy or layout changes (`tools/templates/lead_guide.html`, `lead_guide.css`).
- The Long Form pattern's "What Is In The Guide" list changes. The build fails until the chapter titles match it again. Then check that landing-3's emails 1–7 still match the chapters too, since they cite them by number.
- The theme's Archivo or Newsreader font files change.

A theme `Version` bump alone does not need a rebuild: the guide prints no version.

## Inputs

| Input | Where | Notes |
|---|---|---|
| Copy and layout | `tools/templates/lead_guide.html`, `lead_guide.css` | Edit the copy here. Same palette and fonts as `setup_guide.css`. |
| Theme fonts | `/home/tevis/wp-dfy/wp-content/themes/affiliate-theme/assets/fonts/` | Read in place through `{{FONTS}}`. |
| The landing promise | `inc/affiliate-theme-getresponse.php`, `Affiliate_Theme_Theme_landing_pattern_long()` | The tool reads its `<li>` items under "What Is In The Guide". |

## Tools, in order

One-time setup as in `build_setup_guide.md`: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Playwright drives `/usr/bin/google-chrome`.

1. `.venv/bin/python tools/build_lead_guide.py [--no-copy]` does the following:
   - fills `{{CSS}}` and `{{FONTS}}`
   - checks that every landing bullet appears in the guide
   - prints `.tmp/lead-guide/guide.pdf` and checks that both theme fonts loaded
   - fails over 2 MB (GetResponse's ZIP limit is 10 MB)
   - copies the PDF into the theme's `emails/landing-3/`

   `--no-copy` builds into `.tmp` only, for layout work.
2. Commit the PDF in wp-dfy, using the theme's commit message style and a `Version` bump. Then follow `build_setup_guide.md` from its step 1 to rebuild `affiliate-theme.zip`.

## Verification (all must pass before committing)

1. **PDF:** `pdfinfo` shows Letter and 15 pages. Expect a different page count after copy changes. `pdffonts` lists Archivo and Newsreader as embedded.
2. **Pages:** `pdftoppm -r 55 -png` every page, tile them with `montage`, and review them. Look for widowed headings, a short list split across a page break (give it `class="keep"`), clipped wireframe badges, and overflow. Each chapter starts on a new page, so a short last page at the end of a chapter is expected.
3. **The emails that ship it:** build landing 3's download on the dev site (the **Email sequences** check in the theme's CLAUDE.md). Confirm that `01-your-guide.zip` holds `index.html` and a `guide.pdf` byte-identical to the theme's.
4. **GetResponse:** after the upload, the guide button in landing-3 email 1's preview opens the PDF. This has not been checked yet (see Known quirks).

## Known quirks

- **Chrome clips anything that crosses into the page margin.** The chapter 2 wireframe starts at the left margin, so its number badges sit inside its wide left padding. Badges positioned outside it were cut in half.
- **Chrome embeds the variable fonts as Type 3**, as with the setup guide, which is why the PDF is about 800 KB for text alone. Poppler's "Bad bounding box in Type 3 glyph" warnings are harmless.
- **It is unconfirmed whether GetResponse hosts a PDF from an uploaded ZIP.** The Upload from ZIP dialog says it uploads "all your images and files" to Files and images, and the email links the file by its bare name, `guide.pdf`. If the first real upload shows the link broken, host the PDF elsewhere: the buyer's Media Library is the fallback. Change landing-3 email 1 and the theme's ZIP builder to match, and record the result here.
