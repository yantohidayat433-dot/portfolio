# Portfolio site — working notes for Claude

Single-page portfolio for designer Vika Ivanova. Everything lives in one
`index.html` (inline `<style>`/`<script>`, no build step, no framework).
Images in `images/`, video in `videos/`. Deploys to GitHub Pages.

This file exists so that routine case-study updates (new PDF, new text,
new crop) don't require re-deriving the same conventions from scratch
each time. Read it before touching a `.case` section.

## Git workflow

- Work happens on a feature branch (currently
  `claude/portfolio-details-mobile-or528z`), commit freely there.
- **Only fast-forward `main` and the GitHub Pages branch
  (`claude/portfolio-github-pages-u9oflw`) when the user explicitly says
  "Публикуй" (or an obvious variant).** Before publishing: `git fetch`,
  then `git merge-base --is-ancestor origin/main origin/<feature>` to
  confirm a clean fast-forward, then push the feature branch's tip onto
  both `main` and the pages branch. Never merge/rebase/force-push.

## Bilingual content system

Every translatable text node carries a `data-en`/`data-ru` attribute pair
(HTML-entity-encoded, `&lt;br&gt;` for line breaks) plus **literal
rendered inner content that must itself be the EN version** — the site
defaults to English on load, and a `#langToggle` click swaps every
`[data-en]` node's `innerHTML` from the matching attribute. This means:

- When you add or edit a translatable element, the text you put as its
  actual (non-attribute) content **is** the English copy — it is not a
  placeholder that JS fills in on load. Forgetting this leaves Russian
  showing by default even after you "fixed" `data-en` (a real bug from
  this session: the Foundation badge title had correct `data-en` but the
  literal span text was still Russian).
- Nav/next-project "prev/next" style links follow the same pattern.
- There is no language-aware mechanism for `alt` attributes or anything
  outside `[data-en]` — those stay in whatever language they were written
  in regardless of toggle state (e.g. `.project__title-mobile` buttons,
  a retired/hidden mobile caption pattern, are always Russian — fine,
  since they're not visible; don't "fix" them into a half-measure).

## Case page anatomy (`.case`, id `case-<name>`)

Each case is a long vertical scroll of `.case__media` blocks (single
images/video), `.case__row` (2-up, sometimes 3-up), `.case__quote`
paragraphs, and one `.case__intro` block near the top. Structure to
clone when building a new case:

```
.case__media (cover)
.case__intro
  .case__intro-left  → h2 title, tag pills (mobile only), credits text
  .case__intro-right → 2 body paragraphs
.case__media / .case__row (photos)
.case__quote (centered) / .case__quote--right (right-aligned)
...repeat media + quote blocks...
.case__media--ig-ticker (Instagram story cycling, if present)
.case__next (link to the next case)
```

### The credits-text feature (`.case__intro-title-desc`)

A pair of small gray paragraphs under the case title, left column,
pinned to the bottom of that column (flush with the body copy on the
right). Introduced for Basarab, since reused for Foundation — **every
new/updated case should probably get this**, check the PDF for it (it's
the two short lines right under the title, e.g. "Worked in partnership
with the Origin Design team..." / "Developed...").

Each of the two paragraphs needs **four** `<p>` tags, not two — a
desktop and a mobile variant, because the desktop (409px) and mobile
(~347px) columns need different `<br>` breaks:

```html
<p class="case__intro-title-desc case__intro-title-desc--desktop case__intro-title-desc--first" data-en="…" data-ru="…">…</p>
<p class="case__intro-title-desc case__intro-title-desc--mobile case__intro-title-desc--first" data-en="…" data-ru="…">…</p>
<p class="case__intro-title-desc case__intro-title-desc--desktop case__intro-title-desc--second" data-en="…" data-ru="…">…</p>
<p class="case__intro-title-desc case__intro-title-desc--mobile case__intro-title-desc--second" data-en="…" data-ru="…">…</p>
```

Why `--first`/`--second` instead of `:first-of-type`/adjacent-sibling
selectors: with two variants per paragraph, `:first-of-type` only ever
matches the literal first `<p>` in the DOM (one specific element), not
"whichever variant is currently visible" — it silently breaks the
bottom-pin and mobile spacing for one of the two breakpoints. Always use
the explicit modifier classes for margin rules on this element.

If adding this to a case for the first time, also add it to these two
case-scoped rules (search `.case__intro .project__tags-mobile` and the
adjacent `.case__intro { margin-bottom: 3rem }` in the mobile
breakpoint) — they hide the tag-pill list (replaced by credits text) and
give 48px instead of the usual 36px before the next image:

```css
#case-basarab .case__intro .project__tags-mobile,
#case-foundation .case__intro .project__tags-mobile,
#case-NEWCASE .case__intro .project__tags-mobile { display: none; }

#case-basarab .case__intro,
#case-foundation .case__intro,
#case-NEWCASE .case__intro { margin-bottom: 3rem; }
```

### Text column widths — measure, don't assume

Desktop text columns are NOT all the same width, and guessing wrong
produces either visible overflow or needlessly-short line breaks:

- `.case__intro` is a `409px 1fr` grid (confirmed against the Basarab
  PDF: the body-copy column starts 409px from the media column's left
  edge). This is generic/sitewide, not case-scoped.
- `.case__quote` has a shared `max-width: 480px` cap. `.case__quote--right`
  additionally gets `margin-left: calc(var(--media-width)/2)` by
  default, which aligns it with the right half of a true 2-up image row.
- **Basarab's quote blocks don't use that 2-up alignment** — they align
  to the same 409px column as `.case__intro-right`, confirmed by pixel-
  measuring the PDF. Its `.case__quote--right` override also needed a
  **wider** cap (510px, not 480), because that case's PDF column
  measured ~506px wide — the shared 480px cap was clipping it short and
  forcing narrower-than-designed breaks. Don't assume 480px is always
  right for a `--right` quote; measure the specific case's PDF.
- Any such override must be wrapped in `@media (min-width: 901px)` —
  an unguarded `#case-X .case__quote--right { margin-left: … }` beats
  the phone breakpoint's own `margin-left: 0` reset on specificity (an
  ID selector) despite coming first in source order, collapsing the
  quote to zero width on mobile. This was a real shipped bug, caught
  late.

**The reliable way to get `<br>` breaks right**: never hand-wrap text by
eyeballing the PDF and guessing a pixel width. Open the live page in
Playwright, select the real element, measure its actual
`getBoundingClientRect().width`, then greedy-wrap the text against that
exact number using a hidden probe `<span>` with the same
font/size/weight/letter-spacing. See `rewrap_foundation.js`-style
scripts from past sessions (recreate inline, they're short) — this is
the only way that's actually proven reliable across many rounds of "the
line breaks are wrong" feedback. After any text edit, re-run an
overflow check across **all four** combinations (desktop/mobile ×
EN/RU) — RU text often runs longer than EN at the same break points,
and overflow found late (after a few "Публикуй"s) is a much bigger deal
to fix than overflow caught before the first one.

## Image sizing systems

Two different systems are in play, and a case can mix them:

**Desktop, "natural" cases** (Foundation's original, untouched slots):
`.case__media img/video { width:100%; height:auto }` — no forced crop,
image shows at its own aspect ratio scaled to container width.

**Desktop, "fixed 620px" cases** (Basarab, and now Foundation too, via
`#case-basarab .case__media:not(…slideshow):not(…ig-ticker):not(…final-sale), #case-foundation …`):
every non-special `.case__media` is forced to exactly 620px tall, with
`img, video { height:100%; object-fit:cover }` inside it, cropping to
fill. **This rule is `img`-only unless you explicitly add `video` too**
— a video left out of it will fall back to `height:auto` and render at
its own aspect (letterboxed-looking, inconsistent with every photo
around it) rather than crop-filling like the rest of the case. Same
applies to `.case__row .case__media img` (2-up rows) — add `video` there
too if a row ever needs one.

**Mobile** (`.case__media-mobile`, shown only under `max-width:700px`,
the plain desktop `img`/`video` hidden via
`.case__media:has(> .case__media-mobile) > *:not(.case__media-mobile)`):
height is set by an inline custom property, `--mh`, in rem:

```
--mh (rem) = mobile_file_height_px / 48
```

Mobile crop files are consistently 3× supersampled relative to the
actual ~359px CSS card width (1rem = 16px on this site). Common buckets
seen across cases: `13.25–14.375rem` (wide banner, file ≈636–690px
tall), `21.25rem` (near-square, file ≈1020px), `27.5rem` (tall
portrait, file ≈1320px). When told a target "frame" in actual CSS
pixels (e.g. "440px tall"), convert with `rem = px / 16` and sanity-
check it against one of these existing buckets rather than inventing a
new one — 440px turned out to exactly equal the existing 27.5rem
bucket, not a new size.

**"Insert without cropping" requests**: the sitewide default for
`.case__media-mobile` is `object-fit: cover` (crop to fill — the design
assumption is that every mobile crop was pre-composed exactly for its
slot). If a client supplies a full/uncropped image and wants it shown
whole, letterboxed if needed, add a `.case__media-mobile--contain`
modifier class to that one `<img>`/`<video>` (see existing CSS — it
needs `!important`, because the generic 620px-system's own
`object-fit: cover` rule outranks a flat class on specificity and would
otherwise win back). Use the image's real native dimensions as its
`width`/`height` attributes so the browser knows its true aspect.

## Video inside a case

No case had embedded video before Foundation's "light" clip. Pattern
used (deliberately simple, avoids touching any shared JS):

```html
<div class="case__media reveal" style="--mh:14.375rem">
  <video autoplay muted loop playsinline poster="images/foo.webp" width="1920" height="1080">
    <source src="videos/foo.mp4" type="video/mp4" />
  </video>
  <video autoplay muted loop playsinline poster="images/foo-m.webp" class="case__media-mobile" width="1920" height="1080">
    <source src="videos/foo.mp4" type="video/mp4" />
  </video>
</div>
```

Two `<video>` tags (both pointing at the same file is fine — only one is
ever visible, the hidden one doesn't meaningfully cost bandwidth),
mirroring the existing desktop/mobile `<img>` pair exactly so none of
the existing CSS or JS needs to change. (There's a separate, more
complex pattern already on the homepage hero — `data-src-desktop` /
`data-src-mobile` + a `matchMedia` swap in a page-level `<script>` IIFE
— built for genuinely different desktop/mobile video files. Only reach
for that if a case ever needs two *different* video crops; note its JS
currently does `querySelector` (singular), so a second use of that
pattern needs it generalized to `querySelectorAll` first.)

**Encoding**: re-encode whatever's supplied — client exports tend to be
20MB+ raw H.264/AAC. Match the site's existing video weight (~0.5–2MB
for a few seconds): strip audio (`-an`, these are always muted anyway),
`-c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -movflags +faststart`.
Pull a poster frame with `ffmpeg -vf "select=eq(n\,N)" -frames:v 1
-update 1` — check a few frame numbers, the first frame of a moody/dark
clip is often too dark to be useful as a poster; something from a
second or two in usually reads better.

**Testing video locally**: `python3 -m http.server` does **not** support
HTTP Range requests (always returns `200`/full body, no
`Accept-Ranges`), which breaks `<video>` loading in Chromium — you'll
see `networkState: 3` (NO_SOURCE) and `readyState: 0` even though the
file is perfectly reachable by `curl`. Use `http-server` instead
(`http-server -p PORT -c-1`, already on this machine) when verifying
anything with a `<video>` tag. Confirm with
`curl -I -H "Range: bytes=0-100" <url>` → expect `206 Partial Content`.
Note also that Playwright's bundled open-source Chromium may lack H.264
decode support entirely regardless of server — if `networkState`/
`readyState` still look wrong against a range-capable server, that's
this sandbox, not a real bug; verify sizing/poster/markup instead of
chasing actual playback in headless tests.

## Verification checklist (every text or crop change)

1. Serve the repo locally (`http-server` if video is involved, plain
   `python3 -m http.server` is fine otherwise).
2. Playwright: open the case (`[data-case-open="case-X"]` on desktop;
   on mobile use `.locator(...).first().click({ force: true })` — a
   plain `.click()` on the mobile badge can silently no-op).
3. Run an overflow check (hidden-probe greedy measurement, see above)
   across desktop EN, desktop RU, mobile EN, mobile RU — all four,
   every time.
4. Check `naturalWidth === 0` / `img.complete` across
   `#case-X img` for broken image refs.
5. Screenshot anything you changed and actually look at it — an
   overflow check catches text spilling out, it does not catch "the
   crop looks wrong" or "that's letterboxed when it shouldn't be".
6. When a client supplies her own reference crop/screenshot with
   specific wording or pixel sizes, treat it as ground truth and
   implement to match it directly rather than re-deriving/second-
   guessing — but when your own careful, repeated measurement
   contradicts what a screenshot seems to show, it's often a stale-
   browser-cache artifact on her end (same filenames get reused across
   many content-changing commits) rather than a real live bug;
   cache-bust (`?v=N` query bump) and ask for a fresh screenshot rather
   than blindly reverting verified-correct work.

## Known trailing gaps

- Foundation's mobile-RU credits/body/quote `<br>` breaks were derived
  by rewrapping the RU-desktop wording against the real mobile
  container (no RU mobile PDF was supplied for that round) — if/when an
  actual RU mobile mockup shows up, re-check those breaks against it
  rather than assuming the rewrap is final.
