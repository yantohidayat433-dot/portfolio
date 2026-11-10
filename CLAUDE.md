# Portfolio site — working notes for Claude

Single-page portfolio for designer Vika Ivanova. Everything lives in one
`index.html` (one `<style>` in `<head>`, plain-JS IIFEs at the end of
`<body>`, no build step, no framework). See README.md for the layout of
the file. Keep it that way: no narrative comments (this file is where
the "why" lives), one short comment per CSS section / JS module, no
hidden or retired markup — delete it instead of `display:none`-ing it.
Images in `images/`, video in `videos/`. Deploys to GitHub Pages.

**`UI-KIT.md` is the design-system reference** (grid, type, colours, buttons,
spacing, slot sizes, motion, new-case checklist; Basarab is the template for
new cases). Read it before building or restyling anything, and update it in
the same commit when a token changes.

**No hanging short words, ever** (client rule, Nov 2026): every RU
preposition/conjunction/particle (в, к, с, и, а, о, у, на, не, по, за, из,
от, до, для, при, без, под, что, как, но, же, ли, ту…) and every EN
article/short preposition is glued to the next word with U+00A0, in every
variant (desktop, mobile, `data-en`, `data-ru`), whether the line ends at a
hand-placed `<br>` or wraps naturally. Check new copy for it before
committing. (As of Nov 10 the RU copy is clean; ten EN `data-en` lines in
the older cases still end in a/the/of/and/with before a `<br>`.)

This file exists so that routine case-study updates (new PDF, new text,
new crop) don't require re-deriving the same conventions from scratch
each time. Read it before touching a `.case` section.

## Git workflow

- Work happens on a feature branch (the session's designated
  `claude/...` branch), commit freely there.
- **Only fast-forward `main` and the GitHub Pages branch
  (`claude/portfolio-github-pages-u9oflw`) when the user explicitly says
  "Публикуй" (or an obvious variant).** Before publishing: `git fetch`,
  then `git merge-base --is-ancestor origin/main origin/<feature>` to
  confirm a clean fast-forward, then push the feature branch's tip onto
  both `main` and the pages branch. Never merge/rebase/force-push.

## Bilingual content system

Every translatable text node carries a `data-en`/`data-ru` attribute pair
(HTML-entity-encoded, `&lt;br&gt;` for line breaks) plus **literal
rendered inner content that must itself be the RU version** — since
Nov 2026 the site opens in Russian (`isRu = true` in the toggle IIFE,
`#langToggle` reads «Читать на английском»), and
a click swaps every `[data-en]` node's `innerHTML` from the matching
attribute. This means:

- When you add or edit a translatable element, the text you put as its
  actual (non-attribute) content **is** the Russian copy — it is not a
  placeholder that JS fills in on load. Forgetting this leaves English
  showing by default even after you "fixed" `data-ru`.
- Cursor labels carry all three: `data-cursor-label` (= RU, the default),
  `data-cursor-label-en`, `data-cursor-label-ru`. The mobile pill's
  `.lang-fade` spans likewise hold the RU text literally.
- A link inside a swapped paragraph must not live inside the swapped
  node's innerHTML (the swap would recreate it and drop its hover-colour
  listeners): split the paragraph into a `[data-en]` text span plus a
  `[data-en]` `<a>` (see the third bio paragraph, `.intro__p-part` +
  `.intro__link`).
- Russian copy always uses «ё» (её, ещё, моём, учёных, вёрстки…), even
  if a client PDF spells it with «е».
- Nav/next-project "prev/next" style links follow the same pattern.
- There is no language-aware mechanism for `alt` attributes or anything
  outside `[data-en]` — those stay in whatever language they were written
  in regardless of toggle state. The toggle also sets `<html lang>`.

## Type tokens (Nov 2026, client-approved)

Interface text is one serif (Oceanic Text), tracking 0 everywhere
(`--tracking-serif`/`--tracking-sans` are 0; animation artwork keeps its
own 2% rule), one gray `#7F7F80` (`--color-muted`) for links, credits and
"Смотреть". Desktop: body, links, buttons, cursor label 17/145; credits
14/145; headings 24/145. Phone (fluid rem, 1rem = 16px at 375): body and
links 1rem/1.45, credits .875rem/1.45, headings 1.5rem/1.25. The lang
toggle is an ordinary gray pill in the pickColor swatch list (no
orange/purple state colours any more). Hand-broken sidebar copy and
desktop credits are `white-space: nowrap` so a subpixel-long line can't
add a stray wrap.

Spacing system (desktop, Nov 2026): 8px between paragraphs everywhere
(sidebar, project descriptions, case intro, case quotes), 12px between
credits, 4px between pill buttons (contacts, articles), same on phone
(.25rem).

Hover palette (`PALETTE` in the swatch IIFE) is the client's 35-pair
sheet from `buttons.pdf` (Nov 2026), extracted from the PDF vectors —
re-extract the same way if she sends a new sheet. The mobile "Почитать
обо мне" pill is pink `#FFD2EC` with deep-sage `#4F7268` text, inverted
while open (logo sage `#A5C1BA` on pink is only 1.4:1).

## Laptop / wide-screen layout

- Project rows (main page): the 606px description column is fixed and
  the title column gives way (`minmax(0,1fr) 606px`). 701–1247px: title
  stacks above the copy; 901–1027px additionally swaps in the
  `project__desc-p--mobile` line-break variants. Desc paragraphs are
  `nowrap` on desktop so only the hand-placed `<br>`s break lines.
- Case intro: title column `min(409px, max(350px, 100% - 606px))`, same
  value for `.case__quote--right` margins; 901–1251px stacks the intro
  and zeroes the quote offset. Case body/quote copy is `nowrap` ≥901px.
- Verified with the wrap checker at 760, 905, 1000, 1024, 1100, 1200,
  1251, 1253, 1280, 1366, 1440, 1920 (+ phones): no stray wraps.
- Past 1440px the page is centred; a wheel gesture over the empty side
  fields (they belong to <body>, which never scrolls) is forwarded to the
  visible main column (`.projects` or the open `.case`), ≥901px only.

## Sidebar (bio) and logo

Order per the RU PDF (Nov 2026): three bio paragraphs (third ends in the
Telegram-channel pill link), squiggle, `.knowledge` (heading + two article
pills), divider, contacts, lang toggle. Contacts since Nov 10: «Написать
мне» (`https://t.me/Ivanvika`) and «Почта» (`mailto:vknkta@yandex.ru`) only.
Instagram and «Скачать PDF» were removed until the client sends links; their
markup is in `UI-KIT.md` §4 and their CSS (`.contact__pdf-link`, the phone
nth-child `order` rules that put Instagram second) was kept so pasting them
back is enough. The lang toggle is hidden with the `hidden` attribute
(`.lang-toggle[hidden]` forces `display:none`, the toggle IIFE still binds):
the one sanctioned exception to "no hidden markup", at the client's request,
so it can come back by deleting the attribute. Inline pills (`.intro__link`, `.knowledge__link`) use
`box-decoration-break: clone` plus `padding: .132em 0` so each line's plate
fills the line box and two-line plates touch. Desktop vertical rhythm was
pixel-matched to the PDF (ink rows within ~1px). Articles link to Skillbox Media; the Telegram-channel
pill links to `https://t.me/+7yJ8wf4p_BtjMjg6`.

Logo: rests bold pink (`#FFD2EC`, 2px same-colour stroke); hover (and the
open about sheet on phones) turns `#A5C1BA` with a 3px stroke. 3.5px
started closing the counters of a/o at 190px wide.

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

**Case spacing is one system, never per case** (client, Nov 10: "if I
change a distance in one case it must change in the others"). Defined once
on the generic classes, with no `#case-…` overrides: media butt-joined
(`.case__media`/`.case__row`/`.case__col` have no gaps or margins, desktop
and phone); text 32px below media and 48px above the next (`.case__intro`,
`.case__quote`, ≥701px; phone 1.5rem/3rem); intro and quote copy capped at
512px; `.case__quote--right` aligned to the intro's body column
(`min(409px, max(350px, 100% - 606px))`, zeroed ≤1251px); case nav rule 48px
below the last media, its pills 24px below the rule at the standard button
look (17/145, gray on the plate). `#case-…` rules may only set slot heights,
animations and per-case text behaviour (Basarab's 701–1299px natural wrap).
Foundation's stacked pair beside the t-shirt is 2 × 333.5px so it matches the
667px cell. Verified Nov 10: both cases measure identically at 1440, 1100,
800 and 375.

All buttons look the same at rest (client, Nov 10): gray `#7F7F80` on the
`#EAEAEB` plate. «Смотреть →» keeps its blue left-to-right wipe on hover via
two background layers (wipe clipped to text, plate to the padding box), so
its hover rules set two `background-position` values. Project titles on the
home page (24px black) and the pink phone «Почитать обо мне» are not buttons
in this sense; «Скоро будет кейс» is a status, no plate.

### Text column widths — measure, don't assume

Desktop text columns are NOT all the same width, and guessing wrong
produces either visible overflow or needlessly-short line breaks:

- `.case__intro` is a `409px 1fr` grid (confirmed against the Basarab
  PDF: the body-copy column starts 409px from the media column's left
  edge). This is generic/sitewide, not case-scoped.
- `.case__intro-right p` and `.case__quote` share a 512px cap (Basarab's
  Figma text boxes), and `.case__quote--right` aligns to the same 409px
  column as `.case__intro-right`, for every case (Nov 10).
- If a case ever genuinely needs a different column, any such override
  must be wrapped in `@media (min-width: 901px)` —
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

**Desktop, "fixed 620px" cases** (Foundation via
`#case-foundation .case__media:not(…slideshow):not(…ig-ticker)…`; Basarab
has its own simpler block, see below):
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

## Basarab (Figma rebuild, Nov 2026)

Source of truth is Figma, not a PDF: file `shbJVIXDZhWJpeWo9QrzrS`
(«вика иван | сайт»), page «кейс basarab», frame `1:687` (desktop RU,
1440). It lives in the client's Pro team «совместная работа»; the Starter
teams hit the Figma MCP call limit after ~10 calls. Asset URLs come from
`www.figma.com/api/mcp/asset/…` (allowed in the environment). Export each
slot frame with `download_assets` at scale 2 (PNG), never the raw fills —
the frame export is her exact crop. Files `basarab-01…27.webp` follow the
frame order top to bottom; phone-only crops `basarab-m01/m13/m17/m22`
(cover, box, bag, care guide) exist where the object would be tiny on a
phone. Phone layout is mostly ours (2-up rows stack, everything else full
width at its aspect), except where her mobile Figma frames say otherwise
(Nov 2026): the short trio (sneakers, `basarab-07/08/09`) stacks as three
359x340 cards (`basarab-m07/m08/m09`, frames `79:713/721/723` at 3x,
`--mh:21.25rem`), the box is a 359x340 card (`basarab-m13`, frame `79:390`);
the first trio (the woman, `basarab-02/03/04`) stays a row, with 400px
`-400` files in its srcset for the 124px phone cells.
The off-canvas frames around `1:687` (14.1–14.3, stories, banner vertical,
tg basarab) are raw material for animations still to come.

Slot 15 (right of slot 14, the hands-in-hair portrait) is `.case__media--story`:
`videos/basarab-stories.mp4` over a lazy poster `<img>` (`basarab-15.webp` =
frame 0). The live clip (chosen by the client, Nov 9) is the four-story render
from `animations/stories-post/` (built in another session: Figma «Stories»
frames in their order, live story text, #060606 field, 508x600 slot at 2x).
Per the client's reference recording (Nov 9): 1.5s per story, hard cut, the
progress bar fills linearly; each text line then fades in with an 8.6px rise
and no blur, 0.8s each, 0.08s apart, ease-in-out (client, Nov 2026: the same
gentle fade as the Instagram posts; the earlier blur-in rise read as sharp).
Site file comes straight from `render-site.js` (one pass from the page
screenshots: 960x1200 padded to 1016x1200, field 6→7, BT.709-tagged) so it
decodes to exactly #060606; the poster is its decoded frame 0.
An earlier cut of her own 15s clip (hands-in-hair story removed, progress bar
redrawn as 4 segments) was replaced by it. Clip: no audio, faststart,
`data-lazy-play`, no `poster` attribute.

Slot 10 (left of the "Reliable shoes" text slide) is `.case__media--slides`:
four photos stacked (`basarab-10`, then `-10b/-10c/-10d` from Figma section
`53:254` «video 2», 507x600 frames exported at 2x), cross-fading every 2s
(0.6s fade; incoming on top, outgoing drops only after the fade, so no dip).
Driven by the shared `cycle()` IIFE; the slot gets `aspect-ratio` so it keeps
its height on phones where the case's slot height is auto.

Slot 18 (Instagram posts) is a `.case__media--story` clip, `videos/basarab-insta.mp4`
(2030x1240, 6s loop): Figma section `72:252` «insta», frames 14.1–14.3, hard cut
every 2s (her reference cut every 0.7s; she found that and then 1.5s too fast), and after
each cut every post's text lines fade in (opacity only, no blur, 8px rise, 0.8s
each, 0.08s apart, ease-in-out: client found the stories' blur-in too sharp here).
Field `#0A0B0D` (client), not Figma's `#141620`: build.py repaints it and re-derives
the cards' corner antialiasing; render.py writes it as (11,13,15) so the BT.709-tagged
H.264 decodes to (10,11,14), the closest it can hold. Built in
`animations/insta-posts/` the same way as stories-trio: `build.py` replaces the
text with her raw fills recomposed at the Figma geometry (the New Collection
pattern is her SVG, rendered at 2x) and cuts one flat-colour sprite per line from
the export-vs-clean difference; `render.py` animates. In Figma's frame 14.1 the
first post's white header box starts 1px lower than in 14.2/14.3, so it flickered
on every cut; build.py takes rows 230–245 of that card from 14.2. Opens 1s into
frame 1; the poster `<img>` (`basarab-18`) is that frame.

Slot 26 (three stories, 1015x600) is a `.case__media--story` clip,
`videos/basarab-stories-trio.mp4` (2030x1200, 5s loop): Figma section `68:106`
«Stories», slides `68:44` then `4:686`, one hard cut and loop; each story's bar
has two segments (one per slide, 4px gap at 2x) and fills the current one over its 2.5s slide, and its text lines fade in like the Instagram posts
(opacity, 7.7px rise, no blur, 0.8s each, 0.08s apart). Field written as 7 so it
decodes to #060606. Built in
`animations/stories-trio/`: `build.py` splits her 2x story exports into a clean
background (progress line blended out, text replaced by her raw fills recomposed
at the Figma geometry) and one flat-colour sprite per text line (alpha from the
export-vs-clean difference; her text fonts, PP Right Grotesk Medium and Noi
Grotesk, aren't in the repo), `render.py` animates them in numpy. Settled frames
match her exports to ~1.5/255. The clip opens 1s into slide 1 and the poster
`<img>` (`basarab-26`) is that frame as decoded. Encoded BT.709 with tags: the
first, untagged encode (ffmpeg's BT.601 maths, read as BT.709 by browsers)
shifted warm tones ~5/255 vs the poster, a visible colour jump when it started.

Layout: media are butt-joined (no gaps anywhere); full-width slots 620px,
rows and `.case__media--600` 600px, `.case__row--short` 427px; 32px from
media to text, 48px from text to media (intro and quotes, ≥701px), 48px
to the nav rule and 24px below it. Figma's 1px x-offsets (416/418) and the
624px-tall slot were her slips: the site aligns to the column and the slot
is 620. Credits stay `--color-muted`, not Figma's `#898989`.

Desktop RU breaks are copied from Figma (longest line 511px of 512), so
at 701–1299px, where the column is narrower, the desktop variants drop
their `<br>`s and wrap naturally; every RU short word (в, к, с, и, не,
при, ту…) and EN article/preposition is glued to the next word with a
U+00A0, and every `<br>` is preceded by a space so hiding it can't fuse
words. EN breaks are greedy-wrapped with the same no-hanging rule.

## Video inside a case

Basarab's three clips have phone files (`*-m.mp4`, ~760px wide, 140–170KB vs
0.4–1MB) picked by a `<source media="(max-width: 700px)">` listed first; the
lazy-play IIFE starts loading 1000px ahead (was 300px, clips lagged on phones).
Headless Chromium can't decode H.264, so it falls through to the desktop
source too in tests; real phones stop at the first.

Case videos must not load while their case is hidden (they used to, and
starved the home-page hero of bandwidth: 7.3MB on first load instead of
2.3MB). Pattern: no `autoplay`, `preload="none"`, `data-lazy-play`; the
lazy-play IIFE starts them when they come within 300px of the viewport and
pauses them when they leave (hidden variants never intersect, so they never
download):

```html
<video muted loop playsinline preload="none" data-lazy-play poster="images/foo.webp" width="1920" height="1080">
  <source src="videos/foo.mp4" type="video/mp4" />
</video>
```

The home-page hero is the only `autoplay` video. It picks its file with a
`<source media="(max-width: 700px)">` pair (phone file first), so each
device downloads only its own; its IIFE swaps the poster, reloads on a
breakpoint change and retries `play()` on the first tap/click (iOS Low
Power Mode blocks autoplay).

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

## Foundation "goals" card stack (`.case__media--goals`)

The "goals of the foundation" slot in `#case-foundation` is a live
animation, not an image: four cards stack over each other on a loop
(next card rises from the dark, grows to full size and covers the
previous one, which shrinks back and dims), and on arrival each card
lights its tab and lifts its number/headline in.

- Iterate in the sandbox first: `animations/foundation-goals/stack.html`
  (assets in `animations/foundation-goals/src/`), then port to
  `index.html`. `animations/foundation-goals/index.html` is the older
  plain-scroll variant, kept for reference.
- Each card is laid out in Figma's own 1376x680 px space and scaled to
  the frame by JS (`--s`); the frame is the case slot itself (620px
  desktop, `--mh` on phones), gutters scale with width via `cqw`. Card
  size per the client's reference (Nov 2026): 860px of a 1015px frame
  (77.5/1015 side inset on `.goals-scroller__track`), vertically centred.
  Frame background `#0E0E0E`, dimming veil `#0A0A0A` (neutral, per
  client). Timing: HOLD 1360ms, MOVE 850ms, CSS light/rise transitions
  0.7–0.85s (all ~15% faster than the original 1600/1000).
- Photo-to-dark ramps are per card, inline on `.goal__shade`, sampled
  from the client's approved card renders. When she sends a new render,
  re-fit against it (photo position via NCC, ramps by column ratio)
  rather than eyeballing.
- In `index.html` every component selector is prefixed with
  `.goals-scroller` (the generic `.case__media img` rule otherwise wins),
  and the slot is excluded via `:not(.case__media--goals)` from the
  Foundation 620px `img/video {height:100%}` rule. It also resets
  `font-feature-settings` because the site's global `dlig` turns on
  PP Fragment's ct/st ligatures.
- **Performance:** everything static on a card (photo, shades, glows,
  frosted inactive tabs, label, dot, arrows, rule) is baked into one image
  per card (`images/foundation-goals-card-N.webp`, 1.5x of 1376x680); only
  the number/headline and the tabs' white fill + text are live. The live
  version (8 huge glow layers + 16 `backdrop-filter`s under moving cards)
  stalled real browsers mid-transition. If a card's look changes, rebuild it
  in the sandbox and re-bake (render each `.goal__stage` with texts hidden).
  The card motion is Web Animations of transform/opacity only (keyframes
  sampled from the same `look()` path, rebuilt on resize, paused off-screen),
  so it runs on the compositor and a busy main thread can't make it stutter
  (a per-frame rAF `style.transform` loop still hitched in real browsers).
  The veil sits beside `.goal__stage`, not inside its scaled rounded clip, so
  dimming doesn't repaint the card. Only tab/headline lighting is left to a
  rAF loop reading the animation's `currentTime` (next frame requested
  first, try/catch); it starts at the latest 2.5s after load even if an
  asset is slow.
- Tabs light via a background-color transition on the tab itself. Don't
  go back to an opacity-animated overlay inside the `backdrop-filter`
  box: Chrome painted it in patches.
- Local testing: the site is password-gated; set
  `localStorage['portfolio-unlocked'] = '1'` (e.g. Playwright
  `addInitScript`) before loading, then open via `/#case-foundation`.

## Foundation "We light the way" light slide (`.case__media--light`)

Desktop-only CSS animation in the `foundation-03` slot (phones keep the
static `foundation-m3` crop via the usual `.case__media-mobile` rule).
The glow is the client's own shape (`images/foundation-light-shape.webp`)
placed exactly as on her slide — transform found by optimisation against
the slide: 2724.27px wide, `translate(-738.65px, 97.05px) rotate(-3.762deg)`,
opacity .819 — then a base layer sways/swells and a screen-blended copy
flares in and out. Copies must stay tight to the base edge: their faint
yellow fringe turns olive over the dark background if it strays above it.
Text: Glare 20px / 98% / 6% tracking, `mix-blend-mode: difference`,
nudged `translate(1px, .5px)` for optical centring (measured on the caps;
re-measure if tracking changes). A left-to-right glint is an exact copy of
the base shape seen through a wide bell-shaped mask window that slides
across (outer box moves, inner box counter-moves) — keep the window soft:
a narrow, flat-topped band read as patchy "clumps" of light.
Sandbox: `animations/foundation-light/index.html`. Same scoping rules as
the goals stack (prefixed selectors, `:not(.case__media--light)` on the
620px img/video rule, `font-feature-settings: normal`).

## Foundation citylight (`.case__media--citylight`)

The `foundation-12` slot (right cell of the "Lectures in August" row) is
the client's street mockup with her two posters rolling **down**
inside the screen (new banner enters from above): hold 2.7s, slide 1s,
7.4s cycle, posters at 90% opacity so the dark panel shows through.
The street is her own clip with the trees moving
(`videos/foundation-citylight-street.mp4`, 1008x1344, re-encoded
**ping-pong** — forward then reversed — so the loop has no jump; poster
frame `images/foundation-citylight-street-poster.webp` = frame 0, also
the box's CSS background until the video plays). Her clip is the old
still scaled ~0.83 and shifted, so the screen panel was re-mapped onto
the clip's 1246x1662 frame: left 31.22%, top 26.55%, w 37.22%, h 50.19%.
If she re-exports the clip, re-measure the panel bevel. No glass layer
(client asked for none). Width-fit and bottom-pinned in the slot; works on
desktop and mobile (no separate mobile image).
`.case__row .case__media img` would force `height:100%` on the posters,
hence the doubled-class selector on the strip images. Sandbox:
`animations/foundation-citylight/index.html`.

## Foundation typographic posters (`.case__media--typo`)

The `foundation-04` slot (left cell of the tall 04/05 row, beside the
glasses) is five of the client's event posters rebuilt as live type in their
1008x1280 (2x) space: each line placed from its measured ink box, sizes
evened out per style, **2% tracking everywhere** (client's rule; LECTURES is shrunk 0.6% so it still fits between the frame rules), small text
in PP Fragment **Sans Regular** (`'PP Fragment Sans Regular'` family — the
site's `'PP Fragment Sans'` face is Medium), headlines in Glare, the Science
& Art mark is her SVG (`images/foundation-science-art-logo.svg`). Layouts
cross-fade every 2.8s; the new one's lines all rise and fade in together
(no stagger). Contain-fits the slot (640px desktop, `--mh` mobile) so the
16px margins survive narrow windows — cover-fitting cropped the sides. All
selectors prefixed `.case__media.case__media--typo` (row img rules would
otherwise stretch the logo). Sandbox: `animations/foundation-typo/index.html`.

## Foundation Instagram sets (`.case__media--ig-fade`)

Foundation's ig-ticker (4 sets of 3 post mockups, `images/foundation-ig-N.webp`
2000x1222 + mobile `foundation-ig-mN.webp` 1077x690 centre crops) cross-fades
instead of hard-cutting: `case__media--ig-fade` on desktop and
`case__media-mobile--cycle-fade` on mobile, 2.8s per set, 1.1s fade. The
incoming set fades in on top (z-index 2) while the outgoing one stays opaque
underneath and only drops out after the fade (delayed `opacity` transition),
so there's no dip to black. The old hard-cut tickers, slideshow and their
phone cyclers were removed with the old Basarab; only these two cycle() calls
remain.

## Image weight and loading (Nov 2026 audit)

Home cards are `<picture>` (phone `<source media>` + desktop `<img>`), so each
device fetches one file (Basarab's: desktop is Figma `72:314` at 2x, phone is the
middle photo of that triptych, the woman with the chair, 720x823 like the other
phone covers); the citylight video has no `poster` attribute (its
box's CSS background is the same frame) because a poster downloads even while
the case is hidden. Case images: the "Case images" IIFE flips the first three
shown images of a case to `eager` on hover/touch/focus/click of its link (cover
first, alone), then once the case is visible queues all its shown images top to
bottom, two at a time; skipped on Save-Data/2G. "Shown" = the phone crop on
≤700px when the slot has one, else the desktop img. Measured at 9 Mbit/s with
fast scrolling: no image is blank on screen, and the cover is ready when the
open transition ends (~0.9s). Basarab full-width slots without a phone crop
(12, 16, 18, 19, 25, 26, 27) carry `srcset` with a `-1077` file and
`sizes="(max-width: 700px) 359px, 1015px"` (with `100vw` a DPR-3 phone asked
for 1170px and got the 2030 desktop file). The background fill runs on desktop
only: on phones it queued the whole case (~6.7MB) as soon as it opened, ahead
of the clips, which then lagged; phones rely on native lazy loading. UI font is `fonts/oceanic-text.woff2` (40KB, preloaded; the file's
name table says "TRIAL Oceanic Text"). `_headers` was dropped: GitHub Pages
ignores it. Sandboxes in `animations/` load the subset WOFF2s from `fonts/`
(the full PP Fragment OTFs are gone from the repo).

All images are WebP and `loading="lazy"` except the first project cards on
the home page; the Foundation goals cards and light-slide shape are lazy
too (their animations start without them and pick them up). Phone crops
are at most 1077px wide (3x of a ~359px card), desktop slots 2x (~2030px).
The Nov 2 audit re-encoded heavy files at WebP q78–84 by PSNR ≥40dB; outside
Basarab that touched foundation-10, foundation-m15, grid-10, grid-10-mobile and
grid-11-mobile, and foundation-10 visibly lost its card grain (85% of fine
detail), so all five were restored from `83a7d53^` (`?v=2`). **PSNR is the wrong gate for textured
surfaces**: Basarab's first rebuild picked q40–60 by PSNR ≥40dB and the
client saw paper, card, suede and ribbon textures turn to plastic (and a
blocky halo round the logo). Basarab now (31 files, 6.9MB, `?v=4`) uses the
lowest q in 90–98 that keeps ≥99% of the fine detail (std of luma minus a
1.5px Gaussian blur, encoded vs Figma PNG), lossless only if smaller; light
paper/card (box 13/m13, tag 21) needs q96–98. Always eyeball 3–4x crops of
the flattest textured areas before shipping. The logo slot is live
(`.case__media--logo`: `#e7e8de` + `images/basarab-logo.svg` at 37.08%
width, Figma's 188/507), not a raster.
First home-page load is
~2.1MB, most of it the hero video.

## Basarab slot 12 (striped lavender)

Static again (client, Nov 2026): `basarab-12` is the 2x export of Figma frame
`1:730`. An animated textures clip (photos sliding in and splitting into her
striped layouts, Figma section `53:235`) lived here for a while; it's in git
history (`animations/basarab-textures/`, `videos/basarab-textures.mp4`) if she
asks for it again.

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
