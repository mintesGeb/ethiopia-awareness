# TikTok posting kit (manual uploads by MG)

- TikTok versions: spec "platform": "tiktok", 4-5 slides, ~20 s. Follow arrow points at the profile picture.
- One video per story; log every video in tiktok_posted.json (MG uploads by hand; never send the same video twice).
- Captions: start with searchable words ("Ethiopia news today", "Tigray news", "Ethiopia Eritrea"), then 1-2 sentences, source + date, 5 hashtags.

## Hook experiment (started Oct 20, 2026, MG approved; keep brand, map, colours, arrow)
Rotate the opening slide style and record it as "hook" in tiktok_posted.json so views can be compared:
- "number": slide 1 = {"stat": <number exactly as in the source>, "title": <what it means, max ~8 words>}
- "question": slide 1 = {"title": <a factual question the video answers, max ~8 words>} (no body)
- "headline": slide 1 = the usual headline + short body (control group)
Never use a question that implies blame or an unproven claim; the answer must be in the sourced slides.
