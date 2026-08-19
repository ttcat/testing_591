# Work Codex Handoff — Rental Before/After Video

## Goal
Create a polished vertical social video from the existing 5F rental-property real photos and AI staging images in this repo.

The repeated visual pattern should be:

1. Show the **real/original photo** first.
2. A **vertical divider / horizontal reveal slider handle** sweeps smoothly across the image from left to right, revealing the AI-staged version.
3. Hold briefly on the fully revealed AI version.
4. Transition cleanly to the next room/scene.
5. Repeat.

This should feel like the interactive compare UI on the website, but rendered as a video.

## Local project
Expected local repo:

`~/Sites/testing_591`

GitHub repo:

`ttcat/testing_591`

Main branch:

`master`

Source images:

`docs/assets/images/`

Do not delete or overwrite original source images.

## Output
Create at least:

- `docs/assets/video/5f-real-vs-ai-vertical.mp4`
- H.264 MP4, AAC audio only if music is actually added
- 1080 × 1920, 9:16
- 30 fps
- Target duration: ~30–45 seconds
- Optimize for Threads / Instagram Reels / TikTok / YouTube Shorts

Also create the reproducible script/project used to render it, preferably in:

`video/`

For example:

- `video/render.py` using ffmpeg / MoviePy / Pillow, or
- another simple deterministic local rendering workflow

Do not make this dependent on a proprietary GUI editor.

## Visual style
- Clean, warm, restrained, consistent with the website.
- No flashy transitions.
- No fake zooms that distort room geometry.
- No architecture edits.
- Preserve the exact real photo and exact AI image; the video only animates the reveal between them.
- Warm off-white / charcoal labels matching the site.
- Avoid excessive text.

## Scene timing
Suggested timing per normal scene:

- 0.7–1.0 sec: real photo only
- 1.6–2.2 sec: divider sweeps left → right, revealing AI
- 0.7–1.0 sec: fully revealed AI hold
- 0.25–0.4 sec: simple dissolve / fade into next scene

Aim for about 3.2–4.3 sec per scene.

## Slider animation
The reveal should visually resemble a true before/after slider:

- Real photo fills the frame initially.
- AI photo is masked and progressively revealed from left to right.
- A visible vertical divider line travels with the mask edge.
- Add a small circular handle at the center of the divider if it looks elegant.
- Labels may say `真實屋況` on the real side and `AI 軟裝示意` on the AI side.
- Do not animate a random wipe without the divider; it should clearly communicate comparison.

## Crop / framing rules
The source images are landscape but final video is 9:16.

Critical rule: **do not independently crop the real and AI images in a way that breaks alignment.**

For each pair:

- Use the same crop rectangle / scale / position for both real and AI images whenever they are same-camera-angle pairs.
- Prefer a center or manually chosen crop that preserves key architectural reference points.
- If a pair cannot be aligned because the AI image itself shifted composition, do not fake an aligned slider.

## Current AI assets
Existing AI staging images include:

- `5f-ai-staging-living-01.png`
- `5f-ai-staging-living-02.png`
- `5f-ai-staging-dining-kitchen.png`
- `5f-ai-staging-bedroom-1.png`
- `5f-ai-staging-bedroom-2-01.png`
- `5f-ai-staging-bedroom-2-02.png`
- `5f-ai-staging-bedroom-3-bed.png`
- `5f-ai-staging-bedroom-3-kids.png`
- `5f-ai-staging-bedroom-3-office.png`

There may also now be optimized WebP derivatives. Prefer optimized assets for rendering only if they preserve enough quality; final 1080p video does not need the 2–3MB originals if WebP versions are visually equivalent.

## Pairing accuracy — very important
The website previously had some wrong real-photo ↔ AI pairings. Do **not** guess based only on filenames.

Before rendering, visually inspect each AI image and identify the true matching source angle using:

- window placement
- door position
- built-in cabinets
- fan / AC position
- wall edges
- vanishing points
- camera height / perspective

The user has confirmed that, after recent corrections, **all current website pairings are correct except room 2B**, which is a special case.

Use the current website / local source as the starting mapping, but verify before rendering.

## Special case: Room 2B
`5f-ai-staging-bedroom-2-02.png`

This AI output has composition / framing drift relative to the true source photo.

Therefore:

- **Do not use the normal sliding reveal for Room 2B.**
- Instead use a short static comparison treatment, e.g.:
  - real photo full-frame for ~1 sec
  - quick crossfade or clean split-screen to AI image
  - AI full-frame for ~1 sec
- Add a subtle note only if needed: `AI 構圖略有偏移`.
- Do not imply pixel-perfect before/after alignment where it does not exist.

All other scenes should use the normal slider reveal.

## Recommended scene order
Use the strongest and most understandable sequence, approximately:

1. Hero / living room A
2. Living room B
3. Dining / kitchen
4. Bedroom 1
5. Bedroom 2A
6. Bedroom 2B — special static/crossfade treatment
7. Third room as bedroom
8. Third room as Montessori / child room
9. Third room as office / studio

If this makes the video too long, prioritize:

1. Living room A
2. Dining / kitchen
3. Bedroom 1
4. Bedroom 2A
5. Third room bedroom
6. Third room child room
7. Third room office

Do not include repetitive scenes just to increase duration.

## Intro
Keep intro very short: 0.8–1.5 sec.

Suggested text:

`同一個家，可以有很多種生活`

Smaller line:

`南勢角 5F｜真實屋況 × AI 軟裝示意`

Avoid a long logo animation.

## Outro
~1.5–2.0 sec.

Suggested text:

`喜歡這個家？`
`預約現場看房`

Optionally include:

`南勢角・3房2衛・可貓・屋主自租`

Do not expose private contact details unless they are already intended for the public site.

## Music
Optional.

If adding music:

- use royalty-free / user-owned audio only
- restrained warm instrumental
- low volume
- no lyrics necessary

If no suitable legal audio is already available locally, render the first version without music rather than downloading copyrighted music.

## Performance / quality
- Encode for reasonable social upload size.
- H.264 CRF around 18–22 is fine.
- `yuv420p` for broad phone compatibility.
- Use faststart (`-movflags +faststart`) if using ffmpeg.
- No watermark.

## Website integration (secondary)
After rendering the final MP4:

- optionally add a small video preview section to `docs/index.html`
- use `playsinline`, `muted`, `controls` or a restrained autoplay loop only if it does not hurt mobile performance
- **do not auto-load a huge video above the fold**
- poster image should be lightweight

The primary deliverable is the standalone social video; website embedding is secondary.

## Validation checklist
Before committing:

- [ ] All normal scene pairs align correctly.
- [ ] Room 2B does NOT use a fake aligned slider.
- [ ] Real image always appears first.
- [ ] Divider moves smoothly left → right.
- [ ] AI is clearly labeled as AI staging.
- [ ] No fixed architecture is visually altered by the video process itself.
- [ ] 1080×1920 H.264 MP4 plays on iPhone / Safari-compatible players.
- [ ] Output duration is ~30–45 sec.
- [ ] File size is reasonable for social sharing.

## Git workflow
When finished:

1. Keep generated video and render script in the repo.
2. Commit all relevant changes.
3. Push directly to `ttcat/testing_591` `master`.
4. Report:
   - commit SHA
   - output MP4 path
   - final duration
   - final file size
   - exact pair mapping used for each scene
   - any scenes omitted and why
