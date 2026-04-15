# goroyeh56.com — Static Website

Rebuilt from the Readdy.ai prototype. Clean HTML/CSS/JS + PHP contact form.
No WordPress, no database required.

## File Structure

```
goroyeh56/
├── index.html        ← Main homepage (all sections)
├── contact.php       ← Contact form backend
├── .htaccess         ← Apache config (HTTPS, cache, security)
├── css/
│   └── style.css     ← All styles
├── js/
│   └── main.js       ← Interactions, slider, map, bookshelf, form
└── README.md
```

## Sections Included

- **Hero** — Full-screen quote with misty forest background
- **About** — Image slider + bio + tags
- **Photography** — Instagram-style photo grid
- **Travel** — SVG world map with visited countries pinned
- **Bookshelf** — Filterable book grid (All / Reading / Finished / Want to Read)
- **Channels** — Instagram, YouTube, Podcast, Medium, LinkedIn, GitHub cards
- **Blog** — Featured post + recent posts list + Medium card
- **Contact** — PHP-powered contact form
- **Footer** — Nav + social icons

## Deploy to Bluehost

### Option A — File Manager (easiest)
1. Log in to your Bluehost cPanel
2. Open **File Manager** → navigate to `public_html`
3. Delete or backup existing WordPress files (if you want a clean start)
4. Upload all files in this folder into `public_html`
5. Make sure `.htaccess` is uploaded (it may be hidden — enable "Show Hidden Files")
6. Visit your domain — the site should be live!

### Option B — FTP (FileZilla)
1. In Bluehost cPanel → **FTP Accounts**, create or use your main FTP account
2. Connect FileZilla: Host = `ftp.goroyeh56.com`, your cPanel username/password, Port 21
3. Upload all files to `/public_html/`
4. Done!

## One-line config change

In `contact.php`, update line 14:
```php
$TO_EMAIL = 'your-real-email@gmail.com';
```

## Keeping WordPress (optional)

If you want to keep your WordPress blog at `/blog/`, just upload this site to a
**subdirectory** (e.g., `/public_html/new/`) and test it there first, then swap
by moving files to `public_html` root.

## Notes

- No npm, no build step — pure HTML/CSS/JS
- PHP 7.4+ (Bluehost shared hosting supports this by default)
- All external images use your existing WordPress CDN links
- PHP sessions are used for basic contact-form rate limiting
