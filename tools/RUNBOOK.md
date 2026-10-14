# Ethiopia awareness Page: media runbook

Repo: `mintesGeb/ethiopia-awareness` (must be PUBLIC so Facebook can fetch the files).
Facebook Page id `105052697572360` via Zapier app `FacebookV2CLIAPI`.

## Files
- `tools/render_media.py`: renders a text-only explainer reel (1080x1920 MP4, ~25-40 s, soft synthesized
  background pad, no copyrighted images or music) and a graphic card (1080x1350 JPG).
  Spec format is in the script's docstring. `--card-only` renders only the card (fast).
- `tools/fonts/`: Inter + Noto Sans Ethiopic (SIL OFL, see OFL.txt).
- `specs/`: one JSON spec per piece, named `YYYY-MM-DD_<slug>_<lang>.json`.
- `media/`: rendered files that Facebook pulls from. Delete files older than 7 days on every run
  (Facebook keeps its own copy).
- `posted.json`: log of everything published: `{"date","slot","lang","type","headline","source","url","post_id"}`.
  Read it before choosing a story; do not repeat an event posted in the last 3 days. Append after each post.
- `BRAND.txt`: the Page name shown small at the top of graphics ("Be-Aware MG"). The renderer reads it automatically.

## Render
```
python3 tools/render_media.py specs/<file>.json media/            # reel + card
python3 tools/render_media.py specs/<file>.json media/ --card-only
ffmpeg -loglevel error -y -ss 8 -i media/<id>.mp4 -frames:v 1 /tmp/check.jpg   # then look at it
```
Needs ffmpeg, numpy, Pillow (all preinstalled). Always look at one frame (or the card) before posting:
text must not overflow or overlap the source line.

## Writing slides (same neutrality and sourcing rules as the text posts)
- 5-7 slides. Slide 1 = hook title of max ~8 words (plus an optional short body).
- Middle slides: one fact each. Use `stat` only for a number stated in the source.
- Every slide carries the `source` footer (outlet, and report name if any, and date).
- Last slide title = a neutral call (protect civilians / humanitarian access / restore communications /
  independent investigations / peaceful dialogue); body = "Follow for sourced updates from across Ethiopia."
  (Amharic: "ከመላው ኢትዮጵያ ምንጩ የተጠቀሰ መረጃ ለማግኘት ይከተሉን።")
- The renderer adds a small "Follow / for more" arrow (Amharic: "ለተጨማሪ / ይከተሉን") on the last slide,
  pointing at Facebook's Follow button, and shows slide 1 from the very first frame so the thumbnail
  is never blank. Do not change or move either one.
- `kicker` = TOPIC · REGION in caps (e.g. "FOOD SECURITY · TIGRAY & OROMIA").
- `places` (REQUIRED in every reel spec): where the story happened, as keys from `PLACES` in
  tools/render_media.py, max 2, most specific that the source supports (e.g. ["mekelle"],
  ["tigray", "east_hararghe"]). Use [] for a nationwide story. Slide 1 then shows a small outline of
  Ethiopia with a dot per place and the place name; this keeps every thumbnail consistent. If a place is
  missing from `PLACES`, use the nearest listed town or the region, never guess a location. Optional
  `place_label` overrides the label text. Do not add internal region borders.
- No flags, logos, party colours, photos, maps of front lines or casualty imagery (the plain locator
  map above is the only map allowed).

## Publish
1. `git add specs media posted.json && git commit && git push origin main`. Public URL:
   `https://raw.githubusercontent.com/mintesGeb/ethiopia-awareness/main/media/<file>`
2. Reel: `execute_zapier_write_action` selected_api `FacebookV2CLIAPI`, action `page_video`
   (tool_name `facebook_pages_create_page_video`), params
   `{page: "105052697572360", source: <raw mp4 URL>, title: <headline, max 80 chars>, description: <caption>}`.
3. Card with text: action `page_photo` (tool_name `facebook_pages_create_page_photo`), params
   `{page: "105052697572360", source: [<raw jpg URL>], message: <post text>}`.
4. If Facebook reports it cannot fetch the file, wait 30 s and retry once. If it still fails, fall back
   to a text post (`page_stream` with `link_url`) and say so in the report.
5. Append to `posted.json`, commit and push again.
