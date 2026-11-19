# Vika Ivanova — portfolio

Static single-page site, no build step and no dependencies. Deployed with GitHub Pages.

## Structure

```
UI-KIT.md      design system: grid, type, colours, buttons, spacing, slot sizes
index.html     the whole site: markup, one <style> in <head>, scripts at the end of <body>
images/        WebP stills (desktop crops + "-m" phone crops), SVG marks
videos/        muted loops (H.264, faststart)
fonts/         WOFF2: IBM Plex Serif (UI), PP Fragment subsets (Foundation case artwork)
animations/    standalone prototypes of the Foundation case animations (use fonts/)
robots.txt     the site is not meant to be indexed
```

`index.html`, top to bottom:

- **CSS**: fonts → password gate → base → layout (two independently scrolling
  columns) → sidebar → project list → case pages → tablet (≤900px) → desktop
  and tablet (≥701px: captions, dividers) → desktop (≥901px: projects left, bio
  right) → carousels → cases (≥701px) → phone (≤700px) → Foundation case animations.
- **Markup**: password gate, phone top bar, sidebar (bio, articles, contacts,
  language toggle), project list, then one `<section class="case">` per case
  study.
- **JS**: small IIFEs, each with a one-line comment: password gate, Telegram
  webview fixes, hover colours, wide-screen scrolling, language toggle, scroll
  reveal, navigation between the list and cases, case image preloading, image
  cyclers, cursor label, Foundation animations.

## Conventions

- **Language.** The site opens in Russian. Every translatable node carries
  `data-ru` / `data-en` (entity-encoded HTML); its literal content is the
  Russian copy. The toggle swaps `innerHTML` and sets `<html lang>`.
- **Line breaks are designed.** Copy is hand-broken with `<br>` to match the
  layouts; those paragraphs are `white-space: nowrap` so the browser never adds
  its own breaks. Phone copy has separate `*--mobile` variants where the breaks
  differ. In Basarab, short words are glued to the next word with a no-break
  space so laptop widths (where it wraps naturally) never leave one hanging.
- **Images.** WebP, lazy except the first screen. A slot either has a phone crop
  (`.case__media-mobile`, height `--mh` in rem) or a `srcset` with a 1077px file
  for phones; home cards use `<picture>` so each device fetches one file. When a
  case opens, its images are fetched top to bottom in the background.
- **Design system.** See `UI-KIT.md`: IBM Plex Serif only, one size and leading
  set on `body` (1rem/1.45; `1rem` = 16px, fluid on phones), spacing scale
  4/8/16/24/32/40/48 + 15px frame, colours as `:root` tokens, motion 0.15/0.3/0.6s.

## Local preview

```bash
npx http-server -p 8080 -c-1
```

The site is behind a password gate (a SHA-256 hash in the first script). For
local testing set `localStorage['portfolio-unlocked'] = '1'` in the console.
Use `http-server` rather than `python -m http.server` when checking video: the
latter doesn't support range requests.
