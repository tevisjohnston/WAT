#!/usr/bin/env python3
"""Capture the WordPress admin screen-shots for SETUP-GUIDE.pdf from the wp-guide test site.

wp-guide is a buyer-style install with the theme uploaded from a zip; --site wp-test
drives the dev site instead.

Logs in as user 1 with auth cookies minted by WP-CLI inside the container, so no
password is needed; the session token is destroyed again on exit. Every value
that would identify the test install (the site name, the sending domain and its
DNS record names, the From line, the Reply-to, mailing and admin addresses, the
affiliate URL, page statuses) is replaced in the DOM before the shot and never
saved.

The Activate shot switches the site to twentytwentyfive and back. The theme's
seeder is guarded by the affiliate-theme_pages_created flag, which this tool
checks first, so switching back creates no pages.

Usage:
    .venv/bin/python tools/capture_setup_screens.py [--site wp-guide|wp-test] [--only 05-settings ...]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

# Container and host per site; main() sets CONTAINER, HOST and BASE from --site.
SITES = {
    "wp-guide": ("wp-guide-wordpress-1", "wp-guide.affiliatemarketconnect.com"),
    "wp-test": ("wp-test-wordpress-1", "wp-test.affiliatemarketconnect.com"),
}
CONTAINER, HOST = SITES["wp-guide"]
BASE = f"https://{HOST}"
WAT = Path(__file__).resolve().parent.parent
OUT = WAT / ".tmp" / "setup-guide" / "screens"

SITE_NAME = "My Site"
SITE_URL = "https://yoursite.com"
SAMPLE_DOMAIN = "yoursite.com"
SAMPLE_EMAIL = "you@yoursite.com"
SAMPLE_ADDRESS = "123 Main Street, Springfield, IL 62701, USA"
SAMPLE_URL = "https://example.com/your-affiliate-link"

# [real, sample] text swaps; main() fills it from the site's own values.
SWAPS: list[list[str]] = []

# Dev page IDs, looked up by slug at start-up.
PAGE_SLUGS = {"landing": "landing-2", "privacy": "privacy"}

MARK_JS = """
([rect, label, pad, side]) => {
  const box = document.createElement('div');
  box.className = 'wat-mark';
  Object.assign(box.style, {
    position: 'absolute', zIndex: 2147483646, pointerEvents: 'none',
    left: (rect.x - pad) + 'px', top: (rect.y - pad) + 'px',
    width: (rect.width + pad * 2) + 'px', height: (rect.height + pad * 2) + 'px',
    border: '3px solid #e11d48', borderRadius: '8px', boxSizing: 'border-box',
    boxShadow: '0 0 0 3px rgba(225,29,72,.18)'
  });
  document.body.appendChild(box);
  if (label) {
    const tag = document.createElement('div');
    tag.className = 'wat-mark';
    tag.textContent = label;
    const round = /^[0-9]+$/.test(label);
    Object.assign(tag.style, {
      position: 'absolute', zIndex: 2147483647, pointerEvents: 'none',
      left: (side === 'right' ? rect.x + rect.width + pad + 10 : rect.x - pad - 14) + 'px',
      top: (side === 'right' ? rect.y + rect.height / 2 - 14 : rect.y - pad - 14) + 'px',
      minWidth: '28px', height: '28px', padding: round ? '0' : '0 10px',
      borderRadius: '14px', background: '#e11d48', color: '#fff',
      font: '700 15px/28px -apple-system, "Segoe UI", Roboto, sans-serif',
      textAlign: 'center', whiteSpace: 'nowrap', boxSizing: 'border-box',
      boxShadow: '0 1px 3px rgba(0,0,0,.3)'
    });
    document.body.appendChild(tag);
  }
}
"""


# ---------------------------------------------------------------------------
# WP-CLI
# ---------------------------------------------------------------------------

def wp(*args: str) -> str:
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "wp", "--allow-root", *args],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def wp_eval(php: str) -> str:
    return wp("eval", php)


def mint_session() -> dict:
    php = r'''$exp = time() + 3600;
$t = WP_Session_Tokens::get_instance( 1 )->create( $exp );
echo json_encode( array(
  "token"   => $t,
  "cookies" => array(
    array( SECURE_AUTH_COOKIE, wp_generate_auth_cookie( 1, $exp, "secure_auth", $t ) ),
    array( LOGGED_IN_COOKIE, wp_generate_auth_cookie( 1, $exp, "logged_in", $t ) ),
  ),
) );'''
    return json.loads(wp_eval(php))


def destroy_session(token: str) -> None:
    wp_eval(f'WP_Session_Tokens::get_instance( 1 )->destroy( "{token}" );')


def page_snapshot() -> str:
    return wp("post", "list", "--post_type=page", "--fields=ID,post_status", "--format=csv")


# ---------------------------------------------------------------------------
# Page helpers
# ---------------------------------------------------------------------------

def doc_rect(page: Page, selector: str, frame_selector: str | None = None) -> dict:
    """Bounding box of an element in document coordinates of the top page."""
    if frame_selector:
        frame_box = page.locator(frame_selector).bounding_box()
        box = page.frame_locator(frame_selector).locator(selector).first.bounding_box()
        box = {**box, "x": box["x"] + frame_box["x"], "y": box["y"] + frame_box["y"]}
    else:
        box = page.locator(selector).first.bounding_box()
    if box is None:
        raise RuntimeError(f"not visible: {selector}")
    scroll = page.evaluate("() => [window.scrollX, window.scrollY]")
    return {"x": box["x"] + scroll[0], "y": box["y"] + scroll[1], "width": box["width"], "height": box["height"]}


def mark(page: Page, selector: str, label: str = "", pad: int = 5, frame: str | None = None,
         side: str = "left") -> None:
    page.evaluate(MARK_JS, [doc_rect(page, selector, frame), label, pad, side])


def region(page: Page, selectors: list[str], pad: int = 24, left: int | None = None,
           right: int | None = None, top: int | None = None) -> dict:
    rects = [doc_rect(page, s) for s in selectors]
    x0 = min(r["x"] for r in rects) - pad
    y0 = min(r["y"] for r in rects) - pad
    x1 = max(r["x"] + r["width"] for r in rects) + pad
    y1 = max(r["y"] + r["height"] for r in rects) + pad
    if left is not None:
        x0 = left
    if right is not None:
        x1 = right
    if top is not None:
        y0 = top
    width = page.evaluate("() => document.documentElement.scrollWidth")
    x0, y0 = max(0, x0), max(0, y0)
    return {"x": x0, "y": y0, "width": min(width, x1) - x0, "height": y1 - y0}


def site_swaps() -> list[list[str]]:
    """The site's identifying values, each paired with its sample, longest first."""
    real = json.loads(wp_eval(r'''$s = Affiliate_Theme_Theme_get_settings();
echo json_encode( array(
  "from_name" => $s["from_name"], "reply_to" => $s["reply_to"], "mailing" => $s["mailing_address"],
  "url" => $s["redirect_url"], "blogname" => get_option( "blogname" ), "admin" => get_option( "admin_email" ),
) );'''))
    label = HOST.split(".")[0]
    pairs = [
        [real["from_name"], SITE_NAME], [real["blogname"], SITE_NAME],
        [real["reply_to"], SAMPLE_EMAIL], [real["admin"], SAMPLE_EMAIL],
        [real["mailing"], SAMPLE_ADDRESS], [real["url"], SAMPLE_URL],
    ]
    pairs = [p for p in pairs if len(p[0]) > 2]
    pairs.sort(key=lambda p: -len(p[0]))
    # Resend names records relative to the zone (resend._domainkey.wp-guide);
    # a buyer's apex domain gives the bare names. Both go first: the Site Title
    # may be the label itself.
    return [[HOST, SAMPLE_DOMAIN], ["." + label, ""]] + pairs


def disguise(page: Page) -> None:
    """Hide what identifies the test install."""
    page.evaluate(
        """([name, swaps]) => {
          const a = document.querySelector('#wp-admin-bar-site-name > a');
          if (a) { a.lastChild.textContent = name; }
          document.querySelectorAll('.notice, .update-nag, #wp-admin-bar-comments')
            .forEach(n => n.remove());
          const swap = s => swaps.reduce((t, [from, to]) => t.split(from).join(to), s);
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) { const n = walker.currentNode; n.data = swap(n.data); }
          document.querySelectorAll('input:not([type=password]):not([type=hidden]), textarea').forEach(el => {
            el.value = swap(el.value); el.placeholder = swap(el.placeholder);
          });
        }""",
        [SITE_NAME, SWAPS],
    )


def open_admin(page: Page, path: str) -> None:
    page.goto(BASE + path, wait_until="load")
    page.wait_for_timeout(600)
    disguise(page)


def open_editor(page: Page, post_id: int) -> None:
    page.goto(f"{BASE}/wp-admin/post.php?post={post_id}&action=edit", wait_until="load")
    page.wait_for_function(
        "() => window.wp && wp.data && wp.data.select('core/block-editor').getBlocks().length > 0",
        timeout=60000,
    )
    page.evaluate(
        """() => {
          const p = wp.data.dispatch('core/preferences');
          p.set('core/edit-post', 'welcomeGuide', false);
          p.set('core', 'fixedToolbar', false);
        }"""
    )
    page.frame_locator('iframe[name="editor-canvas"]').locator(".wp-block-post-content, .is-root-container").first.wait_for()
    page.wait_for_timeout(2500)  # ServerSideRender previews, fonts
    disguise(page)


def shoot(page: Page, name: str, clip: dict | None = None) -> None:
    path = OUT / f"{name}.png"
    if clip:
        page.screenshot(path=str(path), clip=clip, full_page=True)
    else:
        page.screenshot(path=str(path))
    print(f"  {path.relative_to(WAT)}")


# ---------------------------------------------------------------------------
# Shots
# ---------------------------------------------------------------------------

def shot_add_new(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/themes.php")
    mark(page, "#menu-appearance > a", "1", pad=2, side="right")
    mark(page, "a.page-title-action", "2")
    shoot(page, "01-add-new-theme", {"x": 0, "y": 32, "width": 575, "height": 300})


def shot_upload(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/theme-install.php")
    page.click(".upload-view-toggle")
    page.locator(".upload-theme").wait_for(state="visible")
    mark(page, ".upload-view-toggle", "1")
    mark(page, "#themezip", "2")
    mark(page, "#install-theme-submit", "3")
    shoot(page, "02-upload-theme", region(page, [".wrap h1", ".upload-theme .wp-upload-form"], pad=40, left=0, right=1366, top=32))


def shot_activate(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/themes.php")
    card = ".theme[data-slug='affiliate-theme']"
    page.hover(card)
    page.wait_for_timeout(300)
    mark(page, f"{card} a.activate", "3")
    shoot(page, "03-activate-theme", region(page, [card, ".theme.active"], pad=24))


def shot_permalinks(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-permalink.php")
    page.check("#permalink-input-post-name")
    # The structure examples and the Optional section's help text print the
    # dev site's own address.
    page.evaluate(
        """([base, url]) => {
          const walker = document.createTreeWalker(document.querySelector('.wrap'), NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const n = walker.currentNode;
            if (n.data.includes(base)) { n.data = n.data.split(base).join(url); }
          }
        }""",
        [BASE, SITE_URL],
    )
    mark(page, "#permalink-input-post-name >> xpath=..", "1", pad=4)
    mark(page, "#submit", "2")
    shoot(page, "04-permalinks", region(page, [".wrap h1", "#submit"], pad=28, left=0, right=1366, top=32))


def shot_settings(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-general.php?page=affiliate-theme-settings")
    for n, field in enumerate(["resend-api-key", "sending-domain", "from-name", "from-local",
                               "reply-to", "mailing-address", "redirect-url"], 1):
        mark(page, f"#affiliate-theme-{field}", str(n))
    mark(page, "#submit", "8")
    shoot(page, "05-settings", region(page, [".wrap h1", "#submit"], pad=28, left=0, right=1366, top=32))


def shot_domain(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-general.php?page=affiliate-theme-settings")
    h2 = "#affiliate-theme-domain"
    table = "xpath=//h2[@id='affiliate-theme-domain']/following-sibling::table[1]"
    check = "xpath=//h2[@id='affiliate-theme-domain']/following-sibling::form[1]//button"
    page.locator(h2).scroll_into_view_if_needed()
    mark(page, table, "1", pad=4)
    mark(page, check, "2")
    shoot(page, "05b-domain", region(page, [h2, check], pad=24, left=160, right=1366))


def shot_sequences(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-general.php?page=affiliate-theme-settings")
    h2 = "#affiliate-theme-sequences"
    page.locator(h2).scroll_into_view_if_needed()
    shoot(page, "05c-sequences", region(page, [h2, "#affiliate-theme-setup"], pad=12, left=160, right=1366))


def _status_all_draft(page: Page) -> None:
    # A buyer who has just activated sees every seeded page as a draft.
    page.evaluate(
        """() => document.querySelectorAll('.wrap ul li').forEach(li => {
             const t = li.lastChild; if (t && t.nodeType === 3) { t.textContent = ' \\u2014 draft'; }
           })"""
    )


def shot_landing_list(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-general.php?page=affiliate-theme-settings")
    _status_all_draft(page)
    h2 = "xpath=//h2[normalize-space()='Your landing pages']"
    ul = "xpath=//h2[normalize-space()='Your landing pages']/following-sibling::ul[1]"
    mark(page, f"{ul}/li[2]/a", "1", pad=4, side="right")
    shoot(page, "06-landing-list", region(page, [h2, ul], pad=14, left=160, right=900))


def shot_editor(page: Page, ids: dict) -> None:
    open_editor(page, ids["landing"])
    page.evaluate(
        """() => {
          const be = wp.data.select('core/block-editor');
          const id = be.getClientIdsWithDescendants().find(c => be.getBlockName(c) === 'affiliate-theme/optin-form');
          wp.data.dispatch('core/block-editor').selectBlock(id);
          wp.data.dispatch('core/edit-post').openGeneralSidebar('edit-post/block');
        }"""
    )
    page.wait_for_timeout(1200)
    # Scroll the canvas so the selected form is in view.
    page.frame_locator('iframe[name="editor-canvas"]').locator(".wp-block-affiliate-theme-optin-form").first.scroll_into_view_if_needed()
    page.wait_for_timeout(800)
    panel = page.locator(".components-panel__body", has=page.locator("button", has_text="Form")).first
    if "is-opened" not in (panel.get_attribute("class") or ""):
        panel.locator("button", has_text="Form").click()
        page.wait_for_timeout(400)
    mark(page, ".components-panel__body.is-opened:has(button:text-is('Form'))", "1", pad=2)
    mark(page, ".editor-post-publish-button__button", "2", pad=4)
    shoot(page, "07-editor-publish", {"x": 0, "y": 0, "width": 1366, "height": 620})


def shot_reading(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-reading.php")
    page.check("input[name='show_on_front'][value='page']")
    # Only published pages are listed. The dev site's published landing page is
    # Centered; relabel it so the example matches the Split page edited in shot 07.
    page.evaluate(
        """() => {
          const s = document.querySelector('#page_on_front');
          const pub = [...s.options].find(o => o.textContent.startsWith('Landing Page'));
          pub.textContent = 'Landing Page \\u2014 Split'; s.value = pub.value;
        }"""
    )
    mark(page, "input[name='show_on_front'][value='page'] >> xpath=..", "1", pad=4)
    page.evaluate("() => { const c = document.querySelector('#blog_public'); if (c) { c.checked = false; } }")
    mark(page, "#page_on_front", "2")
    mark(page, "#submit", "3")
    shoot(page, "08-reading", region(page, [".wrap h1", "#submit"], pad=28, left=0, right=1366, top=32))


def shot_legal_list(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-general.php?page=affiliate-theme-settings")
    _status_all_draft(page)
    ul = "xpath=//h2[normalize-space()='Your legal pages']/following-sibling::ul[1]"
    mark(page, f"{ul}/li[1]/a", "1", pad=4, side="right")
    shoot(page, "09-legal-list", region(page, [ul], pad=16, left=160, right=620))


def shot_legal_editor(page: Page, ids: dict) -> None:
    open_editor(page, ids["privacy"])
    page.evaluate("() => wp.data.dispatch('core/edit-post').closeGeneralSidebar()")
    page.wait_for_timeout(600)
    canvas = page.frame_locator('iframe[name="editor-canvas"]')
    canvas.locator("body").evaluate(
        """(body) => {
          const doc = body.ownerDocument, win = doc.defaultView;
          const style = doc.createElement('style');
          style.textContent = '::highlight(wat-ph){background-color:#fde68a;color:#7c2d12;}';
          doc.head.appendChild(style);
          const ranges = [];
          const walker = doc.createTreeWalker(body, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const n = walker.currentNode, re = /\\[[^\\]]+\\]/g; let m;
            while ((m = re.exec(n.data))) {
              const r = new win.Range(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
              ranges.push(r);
            }
          }
          win.CSS.highlights.set('wat-ph', new win.Highlight(...ranges));
        }"""
    )
    page.wait_for_timeout(300)
    # Below the toolbar: the dev page is published, so its button reads Save,
    # where a buyer's draft reads Publish.
    shoot(page, "10-legal-editor", {"x": 0, "y": 100, "width": 1366, "height": 560})


def shot_privacy(page: Page, ids: dict) -> None:
    open_admin(page, "/wp-admin/options-privacy.php")
    # A native dropdown's open list cannot be screen-shotted, so show it as a list box.
    page.evaluate(
        """() => {
          const s = document.querySelector('#page_for_privacy_policy');
          s.size = s.options.length;
          Object.assign(s.style, { height: 'auto', minWidth: '260px', padding: '4px', backgroundImage: 'none' });
          [...s.options].forEach(o => { o.style.padding = '7px 8px'; });
        }"""
    )
    page.wait_for_timeout(200)
    selected = page.evaluate("() => document.querySelector('#page_for_privacy_policy').value")
    theirs = "#page_for_privacy_policy option[value='%s']"
    mark(page, theirs % selected, "✓ WordPress’s own draft — skip", pad=1, side="right")
    mark(page, theirs % ids["privacy"], "1  Choose this one", pad=1, side="right")
    mark(page, "#set-page", "2")
    shoot(page, "11-privacy", region(page, ["#page_for_privacy_policy", "#set-page",
                                            "xpath=//th[contains(., 'Change your Privacy Policy page')]"],
                                     pad=28, left=340, right=1366))


SHOTS = {
    "01-add-new-theme": ("inactive", shot_add_new),
    "02-upload-theme": ("inactive", shot_upload),
    "03-activate-theme": ("inactive", shot_activate),
    "04-permalinks": ("active", shot_permalinks),
    "05-settings": ("active", shot_settings),
    "05b-domain": ("active", shot_domain),
    "05c-sequences": ("active", shot_sequences),
    "06-landing-list": ("active", shot_landing_list),
    "07-editor-publish": ("active", shot_editor),
    "08-reading": ("active", shot_reading),
    "09-legal-list": ("active", shot_legal_list),
    "10-legal-editor": ("active", shot_legal_editor),
    "11-privacy": ("active", shot_privacy),
}


def run(page: Page, names: list[str], ids: dict) -> None:
    for name in names:
        print(name)
        SHOTS[name][1](page, ids)
        page.evaluate("() => document.querySelectorAll('.wat-mark').forEach(n => n.remove())")


def main() -> int:
    global CONTAINER, HOST, BASE, SWAPS
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", choices=list(SITES), default="wp-guide", help="the site to capture (default wp-guide)")
    parser.add_argument("--only", nargs="*", choices=list(SHOTS), help="capture just these shots")
    args = parser.parse_args()
    CONTAINER, HOST = SITES[args.site]
    BASE = f"https://{HOST}"
    names = args.only or list(SHOTS)
    OUT.mkdir(parents=True, exist_ok=True)

    if wp("option", "get", "stylesheet") != "affiliate-theme":
        print("ERROR: affiliate-theme must be the active theme on the site", file=sys.stderr)
        return 1
    ids = {k: int(wp_eval(f'echo get_page_by_path( "{slug}" )->ID;')) for k, slug in PAGE_SLUGS.items()}
    SWAPS = site_swaps()

    inactive = [n for n in names if SHOTS[n][0] == "inactive"]
    active = [n for n in names if SHOTS[n][0] == "active"]

    session = mint_session()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
            ctx = browser.new_context(viewport={"width": 1366, "height": 900}, device_scale_factor=2)
            ctx.add_cookies([
                {"name": n, "value": v, "domain": HOST, "path": "/", "secure": True, "httpOnly": True}
                for n, v in session["cookies"]
            ])
            page = ctx.new_page()

            run(page, active, ids)

            if inactive:
                if wp("option", "get", "affiliate-theme_pages_created") != "1":
                    raise RuntimeError("seed flag not set; re-activating would seed pages")
                before = page_snapshot()
                wp("theme", "activate", "twentytwentyfive")
                try:
                    run(page, inactive, ids)
                finally:
                    wp("theme", "activate", "affiliate-theme")
                    after = page_snapshot()
                    if wp("option", "get", "stylesheet") != "affiliate-theme" or before != after:
                        raise RuntimeError("site not restored: check the active theme and pages")
                    print("site restored: affiliate-theme active, pages unchanged")
            browser.close()
    finally:
        destroy_session(session["token"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
