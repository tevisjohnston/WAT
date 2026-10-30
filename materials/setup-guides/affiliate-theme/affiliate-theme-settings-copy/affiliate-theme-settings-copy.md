# Affiliate Theme Settings Theme Copy -> `SETUP-GUIDE.pdf`

## Your sending domain

1.	Sign in where you manage the DNS of yourdomain.com. Add each record exactly as shown. If you are using Cloudflare, set each record to DNS only (orange proxy button = off).
2.	Click Verify DNS records. DNS changes can take from a few minutes to a few hours to reach Resend.

You can check the propagation of your domain’s DNS records at <a href=“https://www.whatsmydns.net”>whatsmydns.net</a>. DNS records can propagate in minutes but in some cases they may take up to 24-48 hours to propagate.

## Resend

Create a free account at resend.com. In Resend, open API Keys → Create API Key, choose Full access, and paste the key here. The theme uses the key to add your sending domain and your emails to your Resend account, so a key with Sending access is not enough.

## Funnel

### Landing Pages

Each landing page promises its visitors emails. These emails keep that promise, and every one of them links to your affiliate redirect URL. The theme puts them in your Resend account as one automation for each landing page: the first email goes out as soon as someone signs up, then one a day. Set up the emails for the landing page that you publish.

1. Setting up takes up to a minute. You can see the emails in Resend, under Templates and Automations; their names start with “Affiliate Theme”.
2. The emails match the landing pages as the theme made them. If you change what your page promises, change the emails to match. When you change your affiliate redirect URL, your mailing address or your Site Title, the status says “out of date”: click Update these emails. An update replaces any change that you made to these emails inside Resend.
3. Check the sending limits of your Resend plan before you send a lot of traffic.

### Legal Pages

1. Replace every bracketed placeholder on all four pages: [Your Business Name], [yoursite.com], [you@example.com], [Your Mailing Address], [Your State/Country] and [Month Day, Year]. The Analytics and Advertising section below has a seventh, [Provider Name].
2. Keep each legal page true to your business.
3. Then publish. A published legal page adds itself to the site footer and there is a footer at the bottom of every landing page.

#### If you add analytics, advertising or cookies

The Privacy Policy says you do not sell or share your visitors’ information. That is true only while the site runs no analytics, no advertising pixels and no tracking cookies. If you start using Google Analytics, any advertising platform or cookies, replace its “We Do Not Sell Or Share Your Information” section:

1. Edit the Privacy Policy page.
2. Remove the “We Do Not Sell Or Share Your Information” heading block and the paragraph block after it.
3. Click the + box in the upper left corner.
4. Switch from the Blocks tab to the Patterns tab.
5. Select Affiliate Theme.
6. Insert Legal — Privacy: Analytics and Advertising where the removed section was, after “Who We Share It With”, and replace [Provider Name] with each provider you use.

## Search and Social

The theme writes a description, a social preview and structured data for each page. Three things decide what they say:
1. In Settings → General, the Site Title and Tagline are your home page’s title in Google and in the preview that Facebook, X and LinkedIn show. The Site Icon is the picture a shared link shows when its page has no featured image.
2. Your landing page’s Featured image is the picture shown when someone shares your link. The landing page itself never shows it. Add one with Set featured image in the editor’s Page sidebar. An image 1200 × 630 pixels suits every network.
3. Your landing page’s Excerpt is the description that Google shows under your title. Write one with Add an excerpt… in the editor’s Page sidebar. Leave it empty to use the first paragraph under your headline.

Links to affiliatemarketconnect.com in your posts and pages are marked rel="sponsored nofollow", as Google asks of affiliate links.

