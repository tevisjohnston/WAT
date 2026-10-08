# Build The Affiliate Marketing Blueprint PDF

## Objective

Produce `deliverables/The-Affiliate-Marketing-Blueprint.pdf`, the free lead magnet of `7figure.affiliatemarketconnect.com`. Subscribers get it from the 7figure email service's `WelcomeEmail`, which links `https://7figure.affiliatemarketconnect.com/wp-content/uploads/lead-magnets/The-Affiliate-Marketing-Blueprint.pdf`.

The blueprint replaces a Gamma export, kept for reference at `materials/lead-magnets/The-Affiliate-Marketing-Blueprint/The-Affiliate-Marketing-Blueprint.pdf`. It uses the 7figure brand: Manrope body, Fraunces display, slate with an amber accent, US Letter.

It must keep covering the three things `WelcomeEmail.tsx` (`BLUEPRINT_ITEMS`) promises:
- where to find winning products: Step 1
- the #1 traffic source: Step 4, solo ads, badged "Start here"
- how to go from startup to $5k: the roadmap

The tool does not check these promises. Re-read them after any copy change.

## When to rebuild

- The copy or layout changes (`tools/templates/blueprint.html`, `blueprint.css`).
- An illustration in `materials/lead-magnets/The-Affiliate-Marketing-Blueprint/images/` changes.
- The 7figure theme's Manrope files change.
- An affiliate link changes (Hostinger referral, ClickBank PLR hop link, Udimi).

## Inputs

| Input | Where | Notes |
|---|---|---|
| Copy and layout | `tools/templates/blueprint.html`, `blueprint.css` | Edit the copy here. |
| Illustrations | `materials/lead-magnets/The-Affiliate-Marketing-Blueprint/images/` | The four step PNGs, `clipboard.jpg` (cover), `funnel.jpg` (roadmap opener). `blueprint-cover.jpg` has its text baked in and is not used. |
| Manrope | `/home/tevis/7figure.affiliatemarketconnect.com/wp-content/themes/7_Figure_Affiliate/assets/css/src/fonts/` | Read in place through `{{FONTS}}`. |
| Fraunces | `materials/fonts/fraunces/` | Through `{{FRAUNCES}}`. OFL, from `@fontsource-variable/fraunces` 5.2.9. The 7figure theme declares Fraunces but never loads it, so the live site's headings actually render in Georgia. |

## Tools

One-time setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. It needs Playwright and Pillow, and Playwright drives `/usr/bin/google-chrome`.

1. `.venv/bin/python tools/build_blueprint.py [--out PATH]` does the following:
   - Re-encodes the illustrations to JPEG in `.tmp/blueprint/images/`. Chrome embeds a PNG losslessly, which is why the Gamma export was 2.9 MB.
   - Builds `cover.jpg` from `clipboard.jpg`, moving its drawn checklist down the paper to make room for the live title.
   - Fills `{{CSS}}`, `{{FONTS}}`, `{{FRAUNCES}}` and `{{IMAGES}}`, and fails on a missing image or an unfilled token.
   - **Checks the roadmap arithmetic.** Each `.campaign` block's `data-*` numbers must chain: budget − spend + revenue = the next campaign's budget, and the list grows by the new subscribers. The last campaign must end at `#roadmap`'s `data-goal`, and `data-roi` must equal (goal − start) ÷ start. Every `data-v` cell must show exactly the value the numbers give. **When you change a figure, change its `data-*` attribute and its visible cell together.**
   - Prints the PDF and checks that Manrope and Fraunces loaded. Fails over 2 MB.

   `--out .tmp/blueprint/draft.pdf` builds a draft without touching `deliverables/`.
2. Commit the PDF in WAT together with the template.
3. Publishing is a separate, manual step. Copy the PDF over `/home/tevis/7figure.affiliatemarketconnect.com/wp-content/uploads/lead-magnets/The-Affiliate-Marketing-Blueprint.pdf`, keeping the filename so the WelcomeEmail link keeps working. That file is tracked in the 7figure repo, so commit it there. nginx-proxy caches 7figure (`vhost.d/`), so check the live URL afterwards.

## Verification (all must pass before committing)

1. **PDF:** `pdfinfo` shows 12 Letter pages, all the same size; expect a different count after copy changes. `pdffonts` lists only Manrope (embedded as `ManropeExtraLight-*`, Google's family name) and Fraunces. A DejaVu or Liberation font means a glyph fell back (see Known quirks).
2. **Pages:** run `pdftoppm -r 50 -png` on every page, tile them with `montage`, and review them. Look for:
   - a box or card pushed alone onto a new page
   - widowed headings
   - the cover's step names sitting on their drawn lines
   - no thin dark line at the foot of the page before the roadmap opener

   Step 3 runs over two pages by design.
3. **Links:** scan the PDF for `/URI` entries (decompress the streams). Expect 11: WarriorPlus, Hostinger (with `REFERRALCODE=7V0TEVISJDTJ`), Bluehost, HostGator, Namecheap, GoDaddy, the ClickBank PLR hop link, AWeber, GetResponse, the 7figure SOP page, and Udimi `a/muu3o`.

## Known quirks

- **Manrope and Fraunces have no arrow (→) or check mark (✓) glyphs.** Google's latin subset stops short of them, so Chrome would fall back to DejaVu or Liberation. Draw them with the `.arr` mask and the `.checks li::after` mask instead.
- **A full-bleed section's background leaks.** Chrome paints a 1px sliver of a `page: bleed` section's own background at the foot of the page before it. The roadmap opener therefore puts its image on an absolutely positioned `.bg` child.
- **The cover is pixel-coupled to `clipboard.jpg` (896 × 1152 px).** The checklist crop, scale and position are in `build_blueprint.py` (`CHECKLIST*`). The text positions in `blueprint.html`/`.css` use the same grid (`calc(8.5in * N / 896)`). A replaced image needs all of them re-measured.
- **Fraunces is variable, so Chrome embeds it as Type 3.** Poppler's "Bad bounding box in Type 3 glyph" warnings are harmless.
- **Hosting prices are left out on purpose.** The Gamma version's multi-year prices went stale, so the page says "check the current offer" and budgets about $20 a month.
