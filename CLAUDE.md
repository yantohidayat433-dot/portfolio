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
committing. (Nov 20: every RU short word in the list above plus я, об, во,
со, ко, или, то, над, про, через, ни, да, бы, and every EN a/an/the/of/and/
to/in/on/at/for/with/by/or/as/from/into, is glued in all text and
`data-*` copy; every `<br>` has a space before it, or a U+00A0 when the word
before it is short, so hiding it never fuses or strands words.)

**Phones wrap all text naturally** (Nov 20, client: hand-broken lines were
too short): `br { display: none }` at ≤700 and the sidebar's `nowrap` is
lifted there; the `--mobile` text variants still exist (901–999 uses their
breaks) but on phones they just flow. The old «lines > brs + 1» phone test
no longer applies; check for line-final short words instead.

This file exists so that routine case-study updates (new PDF, new text,
new crop) don't require re-deriving the same conventions from scratch
each time. Read it before touching a `.case` section.

## Release checklist (remind the client, Nov 20)

The client asked to be reminded of these, not to do them yet:

- **When she adds the link to her other site:** favicon and Apple touch icon
  (`<link rel="icon">`, `<link rel="apple-touch-icon">`, 180×180); today Safari
  shows a letter and a home-screen bookmark is a screenshot.
- **Before the public release:** link previews for Telegram/iMessage/social
  (`og:title`, `og:description`, `og:image` 1200×630, `twitter:card`), a real
  `<meta name="description">`, the page `<title>`; also consider removing the
  password gate and checking the 404 page.

## Git workflow

- Work happens on a feature branch (the session's designated
  `claude/...` branch), commit freely there.
- **Publish every change right away** (client, Nov 23: «всегда сразу
  публикуй правки, всё равно нужно смотреть визуально на сайте»): after
  verifying and committing, fast-forward `main` and the GitHub Pages branch
  (`claude/portfolio-github-pages-u9oflw`) without waiting for «Публикуй». Before publishing: `git fetch`,
  then `git merge-base --is-ancestor origin/main origin/<feature>` to
  confirm a clean fast-forward, then push the feature branch's tip onto
  both `main` and the pages branch. Never merge/rebase/force-push.
- **`v1-oceanic` is a frozen save point** (Nov 19 2026, commit `3faabff`):
  the site as published with Oceanic Text, kept before the font
  rebuild. Never commit to it or move it. To roll back, restore its tree
  in a new commit on the feature branch (`git checkout origin/v1-oceanic
  -- . && git commit`), then publish as usual, so it stays a fast-forward.

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
  `[data-en]` `<a>` (the bio's Telegram link was built this way until
  Nov 23; see git history for `.intro__p-part` + `.intro__link`).
- Russian copy always uses «ё» (её, ещё, моём, учёных, вёрстки…), even
  if a client PDF spells it with «е».
- Nav/next-project "prev/next" style links follow the same pattern.
- There is no language-aware mechanism for `alt` attributes or anything
  outside `[data-en]` — those stay in whatever language they were written
  in regardless of toggle state. The toggle also sets `<html lang>`.

## Type tokens (Nov 2026, client-approved)

Interface text is one serif, IBM Plex Serif Regular (since Nov 19, was
Oceanic Text; `fonts/ibm-plex-serif.woff2`, Latin+Cyrillic subset, OFL), one
size and leading for everything: `body { font-size: 1rem; line-height: 1.45 }`
(16px; on phones the root rem stays fluid for layout, but text is
`min(1rem, 16px)`: 16px on every phone ≥375 wide, scaled down below so the
359px-column hand breaks hold; client, Nov 20: the fluid 16→18px read too big on
large iPhones, then 15px too small; inputs 16px so iOS doesn't zoom; the «Почитать
обо мне» pill keeps the fluid `1rem`, client asked not to touch it), inherited by every element; `h2` and
`button, input` are reset to inherit. Hierarchy is caps, colour and the
plate, never size. Tracking 0 (no tracking tokens any more; animation artwork
keeps its own 2% rule). Hand-broken sidebar copy and desktop credits are
`white-space: nowrap` so a subpixel-long line can't add a stray wrap.

**UI cleanup (Nov 19, client: «чтобы не было миллион разных размеров»).**
`UI-KIT.md` holds the system: one type size, spacing scale 4/8/16/24/32/40/48
plus the 15px frame, colour tokens in `:root` (`--color-muted` is #69696A since Nov 20, AA contrast on white and on the plate; `--color-ink/-muted/-plate/
-white/-divider/-media-bg/-pink/-sage/-sage-deep/-accent`; no literal colours
in interface CSS), motion 0.15/0.3/0.6/0.85s. The old 17/24/28/14px desktop
layer, the 409/606 caption and intro grids, `.case__quote--right`,
`.project--half/--hero`, the animated desktop «Смотреть», the Instagram/PDF
contact CSS, the purple cursor label and the unused width tokens are gone.
The tablet (701–900) now shares the ≥701 caption and case layer with the
desktop; ≥901 only adds the two-column layout. Verified by pixel diff against
the previous commit: desktop and phone identical except the sidebar squiggle
(now a block with 8px margins: 24/24 instead of 22/20) and the divider after
the last project (client asked for it).

Hover palette (`PALETTE` in the swatch IIFE) is the client's 35-pair
sheet from `buttons.pdf` (Nov 2026), extracted from the PDF vectors —
re-extract the same way if she sends a new sheet. The mobile "Почитать
обо мне" pill is pink `#FFD2EC` with deep-sage `#4F7268` text, inverted
while open (logo sage `#A5C1BA` on pink is only 1.4:1).

## Desktop home layout (≥901px, Nov 19 2026)

Rebuilt after the client's reference, actualsource.work: projects column
left, bio sidebar right (`order: 2`, `max(366px, (100% + 30px)/3 - 39px)`,
442px at 1440, text 436: client asked for 15px narrower than the original 454
on Nov 19; 46px narrower was tried and rejected). Page padding 15px left, 12px right; columns 12px apart; the
sidebar has 3px side padding (so the logo's stroke isn't clipped by its
`overflow-x: hidden`), logo 40px above the bio (client, Nov 19), which makes the bio text start 15px from the media and
the divider end 15px from the window edge: an even 15px frame (client, Nov 19;
24px was tried first). Media column 959px at 1440. One size 16/1.45
(client, Nov 19, after trying 1.2 and 1.3; Plex's hhea box is 1.3em, so
inline pills get `padding: .075em 0` to tile line to line), 8px between
paragraphs (client tried 16px and a first-line indent on Nov 19), 16px
between sidebar blocks and from a project title to its description. The sidebar divider is the light `--color-divider` (15% black), not `#7F7F80`,
with 24px clear above and below (16px gap + 8px margin). Project: media full
column width at 16:10 (959×599 at 1440; 3:2 and 16:9 were tried first; the
cover files are ~1.69:1, so ~2.7% is cropped left and right), 15px, then a caption row: CSS-counter number in a 49px column +
uppercase title (plate kept), description 16px below it, flush left under the number (as on the reference),
then the light gray divider 32px below the text and 24px above the next
cover (none after the last project), no «Смотреть» (client removed it on
desktop home; phone keeps it). Hover cursor «смотреть»/«скоро» on ≥901px:
16px black text on the pink `#FFD0ED` plate, plate 23.2px tall (one line). 901–999px swaps in the
`project__desc-p--mobile` breaks. The tablet adopted this caption system in
the Nov 19 cleanup. Bio (Nov 23, three paragraphs: who she is; what she
does; how she works + «Пишите…»; the Telegram-channel sentence and its pill,
`https://t.me/+7yJ8wf4p_BtjMjg6`, are out «пока») keeps her own desktop line breaks at
≥1330px (her Nov 23 mockup; longest line ~400px, the column is ≥402 from 1311),
wraps naturally across the full column at 901–1329, keeps narrower hand breaks
on the tablet (701–900), and flows on phones. Two break sets in one paragraph:
`<br class="br-wide">` (≥1330 only), `<br class="br-narrow">` (701–900 and
hidden ≥1330), plain `<br>` (both); the media blocks just above the first
901–999 block hide what doesn't apply (never re-show a `br`). The whole sidebar
is at line-height 1.3 on ≥901 (client, after actualsource.work; the one 1.45
leading stays everywhere else), so its pills drop their .075em padding (1.3 =
Plex's glyph box, plates still tile). Glued so nothing splits in natural wrap:
«8 лет работаю», «её до полной», «Ищу смыслы», «вашу команду», «буду рада
познакомиться».

**Phone home (≤700px, Nov 19, after actualsource.work).** 15px (.9375rem)
gutters, topbar logo on the same line; covers full width at 16:10 like desktop (carousels are 4:5 on phones since
Nov 20, see below),
from landscape files (`grid-NN-1077.webp` phone sources, cut from the 2030
desktop files at q90; the old portrait `grid-NN-mobile` covers were dropped,
only 02/03 remain for the cases' «next case» cards); the hero plays
`videos/vocamate-m01.mp4` (864x1080, her phone frame 1's window of the desktop
hero, crf 26) over `vocamate-m01.webp` (`data-poster-mobile`). Caption: counter number in a 3.0625rem column + uppercase title,
1rem/1.45 text, desc 1rem below, 8px paragraphs, no «Смотреть», light divider
2rem below the text and 1.5rem above the next cover. Carousels run on phones
too (tap a half, or drag: since Nov 20 the track follows the finger like an
Instagram carousel, axis locked after 8px so vertical scrolling stays native
under `touch-action: pan-y`; on release it lands on the next slide past 20% of
the width or on a flick faster than 0.3px/ms over the last 100ms, else springs
back; dragging right from slide 1 wraps to the last via the clone), and their «n/x» sits at the
right end of the title row (`.project__count`, added by the carousel IIFE).
Three phone desc paragraphs (Vocamate's second, 3I Tech's, App Insiders')
were re-wrapped greedily at the iPhone 13 column (359px) with short words
glued: their old breaks overflowed and left «Участвовала» alone. The «Почитать
обо мне» pill is unchanged.

Phone cases follow the same system: text flush with the media (the old
.375rem inset is gone, so the column is 359px on an iPhone 13), intro order
title (1rem uppercase, plate) → gray 1rem credits (1rem, then .5rem apart) →
body 1rem below; text .9375rem below media, 3rem above the next. Images keep
their phone crops (`--mh`). With the wider column most hand breaks fit; five
that still overflowed (Basarab's two long quotes, Foundation's two intro
paragraphs and its typography quote) were re-wrapped greedily at 359px with
short words glued; re-check with the «lines > brs + 1» test after any phone
text change.

**Home carousels (all widths, Nov 19, after actualsource.work).** Vocamate's,
Basarab's and Foundation's home cards are `.project__carousel`s (they replaced
the cover links; tablets got them too, with the n/x counter and swipe as on
phones). The carousel has its own 16:10 box and does NOT carry
`.project__media`, whose hover zoom and img rules would hit the animations
inside.

Vocamate (12 slides, Nov 19 rebuild) follows the client's 1:1 slide frames in
Figma file `shbJVIXDZhWJpeWo9QrzrS`, section `112:28385` «vocamate case»,
frames «vocamate 1440 - 1…12» (960×600, exported at 2x = 1920×1200, exactly the
carousel's 16:10). Stills 2–6 and 8 are the exports (`vocamate-sNN.webp` q90 +
`-1077`). Slide 1 is the hero `<video>` itself (`carousel__cell--hero`,
`object-position: 27% 50%` reproduces frame 1's crop). The video slides are
rendered by ffmpeg to sit exactly where the frame puts them, transforms found by
SIFT matching of clip frames against the export (scratchpad `voc2/match.py`,
`render.sh`): 7 = icons clip (Behance v2) 1:1, full width at y 43, on its own
#010101 field (client, Nov 19: Figma's #0E0E14 frame around the clip showed as a
second background; full width so icons sliding in aren't clipped at a hard line);
9 = frame with its static sphere inpainted, sphere clip (v3) at .825
+(166,446) blended *lighten* (clip field #010101 vanishes into the slide's
#0E0E14); 10 = tablet clip (v4, a multi-shot edit; matched on its wide shot,
2–4s) at 1.2932 −(226,20), full bleed (y 8 showed the clip's black top edge);
11 = two cells: the client's own 4:5 clip (`5 (1).mp4`, 2000×2500) on the left,
the right half of the frame export as a still (`vocamate-s11r` + `-540`, Figma
`110:20933`; the v5 icons video there showed its edge, client dropped it);
12 = results tablet (v6) at 1.2 −(62,36), source window x 52–1652, y 30–1030
(Figma's 1.14832 reached the clip's dark right vignette and bottom black rows,
client saw a black stroke on the white shots). Each has a 960-wide
`-m.mp4` phone file and a first-frame poster. Raw Behance 1080p sources live
outside the repo (Kinescope, see above). Cell rules only touch direct children
(`.carousel__cell > img`). Foundation (15 slides, Nov 19 rebuild) follows the
client's 1:1 frames, section `114:28394` «foundation case», «foundation 1440 -
1…15»: stills `foundation-cNN.webp` (q92 + `-1077`; half cells `c04r`/`c09l`
+ `-540`). Slide 3 is now her still (the live light slide is case-only). Live
slots are copies of the case markup in `carousel__cell case__media
case__media--X` cells (their IIFEs init every `[data-typo]`/
`[data-goals-scroller]`/`[data-citylight]`; the copy drops
`.case__media-mobile` and the `#goal-ui` template): 4 left = typo posters
rebuilt from her 480×600 layouts (section `114:28395` «foundation 1440 - 4
video», frames 1–5; generator `fnd/typo.py` in the scratchpad), a
`.typo--480` stage (480×600 space, `#0e0e14`, 1px `#2C2C31` rules, logo SVG at
75px, `.typo__line--c/--r` for centred/right-aligned lines; Figma sizes and
tracking as-is, 10/28/86px lines nudged 1.5–1.75px down to match her exports
within a pixel; the fit IIFE reads the stage size); 7 = goals stack, card
786×388 at (87,106) like her frame (`.carousel__cell .goals-scroller__track`
inset 87/960, field `#0f0f12`); 9 right = citylight unchanged (her frame places
it the same within 3px); 10 = Instagram sets cross-fading (`--fade-slow`): set
1 is her frame, sets 2–4 are the old mockups warped onto it (SIFT ×1.01501
−(56,20)) with only the post photos swapped in, so the chrome is hers
(`foundation-cig1…4`). On phones the case's `--mh` slot heights must not reach
carousel cells (`.case__media:not(.carousel__cell)`). Split slides overlap their
cells by 1px (`.carousel__slide > * + *`): at half-pixel widths the grey
`--color-media-bg` showed as a hairline between the halves. Slides are exactly
100% wide (no overlap, no z-index swap: raising the incoming slide mid-move made
Safari rebuild layers, a micro-twitch at every switch), and `snap()` floors the
carousel to a width that is a whole number of device px after the page zoom
(`--page-zoom`), on load and resize: on phones the fluid gutters made it 358.81px,
every slide sat on a fractional offset, Safari snapped the layer at the end of
each move and a sliver of the neighbour showed. Motion (Nov 20, client wanted it
«as seamless as Apple»): the track is moved in px; drags follow the finger from
the moment the axis locks (8px, rebased so it doesn't jump), are applied once
per frame, and can catch a slide mid-flight; release, taps and keys run a
critically damped spring (ω 14, ~0.5s) seeded with the finger's speed over the
last 80ms, sampled into Web Animations keyframes so it runs on the compositor;
neighbours ±1/+2 are set eager and `decode()`d after each landing so no image
decodes during a move; the marquee pauses off its slide. Phone polish (Nov 20
audit): the carousel has no tap highlight, no text/image selection, callout or
image drag; its clips pause while it is off-screen (IntersectionObserver) and
play again on return; the loop clone's videos never autoplay: on the last slide
the clone's video is pre-warmed at slide 1's time, and whenever the clone comes
into view (landing on it, wrapping back, dragging past slide 1) both are seeked
to the same time and played together, so the swap is frame-exact; it re-snaps
only when its column really changes width (ResizeObserver), not on the iOS
toolbar's resize events. Cover hover zoom is inside `@media (hover: hover)` (it
stuck after a tap on phones), and `.reveal` blocks no longer carry a permanent
`will-change` (48 always-on GPU layers in a case). **No loop clone any more**
(Nov 20: going 12→1 flashed, the clone's video/image wasn't the live one): to
loop, the first visible slide itself is moved to the end with a transform
(`wrap()`) while the track shows positions count−1…count, and moved back with the
track in the same frame on landing (`unwrap()`); same element, nothing to swap.
**Loading:** only each set's first slide has real `src`; every other carousel
`<img>` carries `data-src`/`data-srcset` (native lazy loading would fetch the
whole horizontal track) and `warm()` fills them in: the next slide once the
carousel is within half a screen, the previous and +2 once it is on screen.
Phone first load went 4.2MB → 1.8MB. Phone-only images (56 files, list from a
phone crawl minus desktop 1x/2x and tablet crawls; `phone/opt.py`) were
re-encoded at the lowest WebP q keeping ≥98.5% fine detail and luma SSIM ≥.985
vs the previous file, 6.4 → 5.3MB; the grainy Basarab/Foundation textures stay
as they were (AVIF saved only ~10% at equal detail, not worth `<picture>`). Her phone frames have
~16px rounded corners exported over white; `phone/corners.py` (scratchpad)
inpaints them before saving the stills
(`?v=2`). If a case animation
changes, update its carousel copy too. **Vocamate on phones is its own set**
(Nov 20): the client's 12 frames in section `117:36266` «vocamate mobile case»
(1080x1350). Slides carry `carousel__slide--desktop` (hidden ≤700) or
`--phone` (hidden ≥701); the hero slide is shared. The IIFE builds its stops
from visible slides only. Phone files `vocamate-m02…m12` (stills = her
exports at q90; clips 1080x1350, crf 24, sRGB-tagged, first-frame posters;
script `vocm/render.sh` + `vocm/icons.py` in the scratchpad): 5 = archive clip
1 (2048 square) at her window (24,23,1601x2001); 6 = archive clip 2 as is;
11 = archive clip 3 (2000x2500) at (133,260,1691x2114); 10 = v4 at her 1.497
(bezel at y 90–1228) but centred on the screen (x 807), since the clip's
captions are centred and her still's aren't; 12 = v6 at 1.29 (133,32), her
1.2685 nudged in to keep the clip's black bottom rows out; 8 = icons: 0–2.4s a
864x1080 window on the heart, cross-fading into v2 from 3s with its 7x4 grid
cut into cells and placed on her 4x7 grid (centres x 213+218c, y 201+158r,
×0.821, lightened onto #0A0A0F); her document and network icons aren't in the
clip, so heart and search take those two places. The desktop slides' `-m.mp4`
phone files went with this. **Foundation on phones is its own set** (Nov 20):
her 18 frames in section `122:74368` «foundation mobile case» (1080x1350);
stills `foundation-pNN.webp` (her exports, lowest q 84–98 keeping ≥98.5% fine
detail; scripts `fndm/py/` in the scratchpad). The goals slide is the one slide
shared by both sets (desktop 7, phone 8); the others are `--desktop`/`--phone`.
1 = the light slide (`.light-slide--phone`, 1080x1350 stage): her gradient is the
same shape file at 4916x2920, `translate(-2411px,-278px) scaleX(-1)`, opacity 1
(checked against her export to <0.5/255), same drift/spill/sweep, live Glare text
140px/1, 3% tracking, the gold span her 94° gradient; 4 = a `.typo--480` copy;
8 = goals in a tall cell: card at her 5cqw inset, active card 174/1350 from the
top, the previous one peeking 120/1080 above, the next two below dimmed to .72,
so all four show; the card leaving at the back fades out during the move and
reappears at the bottom fading in over 0.6s (card opacity keyframes, tall cells
only), so nothing pops; 11 = a citylight copy 1153 wide (`--citylight-wide`,
her frame's −36px, bottom-pinned); 12 = her 12 Instagram posts (Figma
`122:74229`) cut with a clean 25.6px rounded alpha into three column strips
(`foundation-p12-colN`, 540x3496, her grid's columns, #0f0f12 field), placed
like Basarab's grid (344 wide, 30 apart, tops −230/−130/−30) and drifting
44s per strip, columns 1 and 3 up, 2 down (`.posts-flow`, paused off its slide,
none with reduced motion). **Basarab on phones is its own set too** (Nov 20):
her 17 frames in section `118:36761` «basarab mobile case», `basarab-m01…m17`
(stills = her exports at q92; script `basm/build.py` in the scratchpad). The
carousel IIFE clones the first *visible* slide on every build, since Basarab
has no shared first slide. 8 = the four-story clip (`basarab-stories.mp4`) at
×1.125 −31px, which is exactly her frame (field #060606), `basarab-m08.mp4`;
11 = a still grid of all nine Instagram posts of desktop slide 10 (Figma
`72:252`, post groups exported at 2x) in three staggered columns, 344 wide,
30 apart, tops −230/−130/−30, after her reference `118:36762`; 16 = the six
stories of desktop slide 15 (Figma `68:106`, exported at 3x) on one 4044×1076
strip at her spacing (594.7 wide, 674 pitch, her frame's order), two copies in
`.marquee` sliding left by one strip every 30s (CSS, linear; none with reduced
motion), starting where her frame does (−431). **Phone carousels are 4:5** (Nov 20,
client: 16:10 at 359px was too small): `.carousel__slide--pair` slides (two
480×600 cells, or one still whose halves are separate frames: Basarab 3/12/13,
Foundation 6/12/13/15) are 200% wide on phones and the IIFE pages through
"stops" (one per slide, two per pair on phones; rebuilt on the 700px media
change), so every half is exactly 4:5 with no crop: Vocamate 13, Basarab and
Foundation 21 stops. Everything else is centre-cropped for now, phone `sizes`
are 200vw/100vw so the crop stays sharp; the client will send 4:5 phone frames
for the slides that crop badly (text slides, triptychs, tablets). Goals card on
phones is inset 4cqw. Basarab (16 slides, Nov 19 rebuild) follows the client's 1:1 frames in the
same file, section `114:28393` «basarab case», «basarab 1440 - 1…16» (960×600
→ 1920×1200 at 2x): stills `basarab-cNN.webp` (q94 + `-1077`, textures need
the high q). Animated slots reuse the case animations, placed by SIFT match:
5 = the slot-10 photo series cross-fading in the left half (`carousel__cell--fade`,
1.4s per photo since Nov 19, client asked for faster; cover; her frame shows the first photo ~5% smaller than cover, the other three
only exist at the old crop) + the frame's right half (`basarab-c05r`, `-540`);
7 = the four-story clip at .95717 −(6,−7) on its #060606 field
(`basarab-cb07l`) + right half `basarab-c07r`; 10 = Instagram clip 1:1 cropped
at (56,20) (`basarab-cb10`); 15 = three-stories clip 1:1 cropped at (54,0)
(`basarab-cb15`); each with a `-m.mp4` phone file and a first-frame poster.
The old logo cell and contain-trio CSS went with the old slides. Click on the right half / Enter / → next, left half / ← prev (as
on the reference), looping through a cloned first slide; the cursor plate shows «n/18» (the IIFE rewrites
`data-cursor-label*` and the live label). The title still opens the case.

**Desktop cases (≥901px, Nov 19)** follow the home system: `.case` is an
inline-size container and every slot height is `calc(H / 1015 * 100cqw)` (the
old fixed 620/600/427/333.5/667/640px were for a 1015px column; at 929 they
cropped ~9% off the sides). Intro stacks: uppercase 16/1.45 title (plate),
8px, gray 16px credits (8px apart), 16px, body paragraphs 8px apart; quotes
left-aligned; text 15px below media, 48px above the next. 901–999px swap in
the `--mobile` text variants. Case nav: same 32/24 divider as the home list,
pills 16px uppercase like the home titles. Basarab's natural-wrap rule is now
tablet-only (701–900).

## Laptop / wide-screen layout

- (History: project rows and case intros used to be 409/606 two-column grids
  with 1247/1027/1251px fallbacks; all removed in the Nov 19 cleanup.)
- Verified with the wrap checker at 760, 905, 1000, 1024, 1100, 1200,
  1251, 1253, 1280, 1366, 1440, 1920 (+ phones): no stray wraps.
- 1441–1680px windows (Nov 18: a 14" MacBook's Chrome is 1512 wide and
  showed white side fields) scale the whole 1440 layout with CSS `zoom`
  on `.page`: `--page-zoom` = width/1440, set by the first IIFE after the
  gate, `height: calc(100vh / zoom)`. `.hover-cta` lives outside `.page`
  (fixed, positioned from clientX), so it multiplies its own sizes by the
  same var instead of being zoomed. JS that reads `getBoundingClientRect`
  inside `.page` must divide by the zoom (see goals `fit()`); offset/client
  sizes are already unzoomed. Past 1680px the page is centred (client, Nov 18: full scaling to 1920 made
  body text ~23px; 1680 caps it near 20px); a wheel
  gesture over the empty side fields (they belong to <body>, which never
  scrolls) is forwarded to the visible main column, ≥901px only.

## Sidebar (bio) and logo

Order per the RU PDF (Nov 2026): three bio paragraphs (see the Nov 23 note above), squiggle, `.knowledge` (heading + two article
pills), divider, contacts, lang toggle. Contacts since Nov 10: «Написать
мне» (`https://t.me/Ivanvika`) and «Почта» (`mailto:vknkta@yandex.ru`) only.
Instagram and «Скачать PDF» were removed until the client sends links; their
CSS went in the Nov 19 cleanup, a plain extra `<a>` in `.contact__links` is
enough to bring one back (`UI-KIT.md` §5). The lang toggle is hidden with the `hidden` attribute
(`.lang-toggle[hidden]` forces `display:none`, the toggle IIFE still binds):
the one sanctioned exception to "no hidden markup", at the client's request,
so it can come back by deleting the attribute. Inline pills (`.knowledge__link`) use
`box-decoration-break: clone` plus `padding: .075em 0` (≥701; Plex's glyph
box is 1.3em in a 1.45em line) so each line's plate fills the line box and
two-line plates touch. Desktop vertical rhythm was
pixel-matched to the PDF (ink rows within ~1px). Articles link to Skillbox Media.

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
.case__quote (left-aligned, like the intro)
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
(`.case__media`/`.case__row`/`.case__col` have no gaps or margins); text 15px
below media and 48px above the next (`.case__intro`, `.case__quote`, ≥701px;
phone .9375rem/3rem); case nav rule 32px below the last media, its pills 24px
below the rule, uppercase like the home titles. `#case-…` rules may only set
slot heights, animations and per-case text behaviour (Basarab's 701–900px
natural wrap). Foundation's stacked pair beside the t-shirt is 2 × 333.5 of a
1015-wide column so it matches the 667 cell.

Pill buttons look the same at rest (client, Nov 10): `--color-muted` on the
`--color-plate` plate. Not pills, on purpose: project and case titles and the
case nav (ink on the plate, caps), the pink phone «Почитать обо мне», and
«Смотреть →», which now only lives in the phone «next case» card. «Скоро
будет кейс» is a status, no plate.

### Text column widths — measure, don't assume

Text columns are the full media column (≥701px; intro and quotes are no
longer capped or offset), so hand breaks are limited by the copy, not the
column, except at 901–999px (phone variants) and on phones (359px at 375).
Any per-case column override must be wrapped in `@media (min-width: 701px)`:
an unguarded `#case-X …` rule beats the phone breakpoint's resets on
specificity (a shipped bug once, with the old `.case__quote--right`).

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

**Phone playback lag (Nov 10).** Measured at 4 Mbit/s on an iPhone profile: the
clips started loading only ~1000px ahead and queued behind the case's lazy images,
finishing ~3s after reaching the screen. Now, on ≤700px, the lazy-play IIFE starts
every clip of an opened case as soon as the cover has loaded (or after 1.5s):
`play()` then `pause()` unless the clip is near the viewport, which is the one
trigger iOS reliably loads on. All three Basarab clips are then in before the first
one is on screen. Desktop keeps plain near-viewport loading (heavier files, and the
background image queue). A paused near-viewport clip retries `play()` on the next
`touchend`/`click` (iOS Low Power Mode refuses autoplay). The home hero pauses while
`.projects` is hidden (IntersectionObserver) and resumes on return. Citylight has a
phone file `foundation-citylight-street-m.mp4` (720x960, crf 30, 620KB vs 1.5MB,
visually identical at phone size).

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
Tag colour as BT.709 matrix/primaries but **sRGB transfer**
(`-colorspace bt709 -color_primaries bt709 -color_trc iec61966-2-1`): with a
bt709 transfer tag Safari (and Chrome on macOS) re-maps the gamma of video but
not of the WebP poster, so every clip visibly jumped in tone when it replaced its
poster (client, Nov 19). All tagged clips were re-tagged in place, no re-encode:
`ffmpeg -i in.mp4 -c copy -bsf:v h264_metadata=transfer_characteristics=13
-color_trc iec61966-2-1 -movflags +faststart out.mp4`. Bump `?v=` after.
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
