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

## Content limits on TikTok (added Oct 23, 2026)
- MG confirmed (Oct 23): avoid anything that could break TikTok Community Guidelines. TikTok REJECTED the Dera school drone strike video (2026-10-22_tt_deraschool_en), and the Finarwa drone strike
  video (children killed) got 0 views. Do not make TikTok versions of stories whose main point is people,
  especially children, killed or wounded in strikes or attacks. Keep those on Facebook only.
- Good TikTok topics: aid and health access, displacement and refugees, daily life, travel and security alerts,
  diplomacy and official statements, claims and denials.
- MG must leave at least 2 hours between TikTok uploads, with no more than 3 a day. Suggest times spaced that way.

## Focus (agreed with MG Oct 23, 2026)
- TikTok niche: Ethiopia at the center, plus Horn of Africa issues as they relate to Ethiopia: Ethiopia–Eritrea
  (border, Assab, Red Sea access), Tigray politics and the Pretoria deal, Egypt and the Nile/GERD, the
  Alamein Declaration (Egypt, Eritrea, Somalia, Sudan), Sudan and Somalia where Ethiopia is involved.
- Prefer explainers ("Why does Assab matter?") and both-sides official statements. Always give each side's
  position together. Label state media (Shabait, ENA) as state media and blogs/op-eds as opinion.
- Why: the Aksum video (well-known heritage place, big stakes, nothing graphic) is the best performer by
  views, likes and saves; official-statement videos (UN, Eritrea denial, US Embassy) are next.
- Facebook stays as is: broad human-rights coverage across the country.
- Oct 23: the English Alamein video, posted 3h20m after the Amharic version of the same story, had 0 views after
  3 hours while the Amharic one had 208. Never post two language versions of one story on TikTok on the same
  day; put them at least a day apart.
- Precaution (Oct 24): keep words like "war", "killed", "attack" out of the slide-1 title and the first line of the
  caption; TikTok seems to review conflict-heavy wording more slowly. Use neutral verbs ("trade words", "tensions").
- Oct 24 evening: three new uploads in a row at 0 views (Alamein-en, war of words, jobs visa) while older videos keep
  growing. The jobs video was calm (uploaded via web Studio, not the app), and TikTok offered to boost it (so it passed the policy
  check). Treated as a temporary hold on new uploads: MG confirmed ALL uploads (including the good ones) were via web Studio, so the upload method is not the cause. Plan: pause TikTok uploads 48 h, then ONE test upload through the phone app on Oct 26 afternoon. Meanwhile no deleting,
  no privacy toggles, no engagement from MG's second account. Facebook continues as normal.
- Oct 24 9:30 PM: web Studio shows "Not eligible for For You feed - violates Community Guidelines" on Finarwa
  (drone strike, children killed), "war of words" (Abiy/Shabait/UN envoy quotes, "war" in the opening), and the
  English Alamein (twin of the Amharic one, which is fine: likely treated as unoriginal/duplicate). The calm jobs
  video has no notice but 0 views (likely knock-on from the earlier flags). Lessons: no casualty stories, no
  "war" wording, no second-language copies of a story, and quote-heavy Eritrea/Ethiopia rhetoric is risky;
  explainers that give background (Assab, Alamein-am) and humanitarian stories (Moyale, clinics) pass.
  Check web Studio after every upload for a "Not eligible" notice.
- Oct 24 10:20 PM: the calm jobs/forged-visa video is ALSO "Not eligible". Every upload since Oct 23 8 PM has
  been flagged, while Moyale/Assab/Alamein-am (posted Oct 23 1-5 PM) passed. Either the account is under tighter
  automatic review, or each video tripped its own filter (duplicate; "war"; forged visas / migrant workers may hit
  the human-exploitation policy). Monday test must be the safest possible: humanitarian/aid or cultural story,
  no claims of crimes, no migration-fraud angle, short caption. If that is flagged too, treat it as
  account-level: post on TikTok at most once every 2-3 days for 1-2 weeks and file "Report a problem".
- Oct 25 test RESULT: the WFP food-aid video got 83 views within ~1 hour, so the account is NOT blocked. The flags
  were topic/wording filters on individual videos. Resume: max 2 TikToks a day, 2+ hours apart, calm openings,
  topics from the "passes" list; check web Studio for a "Not eligible" notice after each upload.
  Passes: humanitarian/aid/health numbers, displacement, background explainers, official denials.
  Flagged: casualties, "war" wording, heated government-vs-government quotes, second-language duplicates,
  migration fraud/trafficking angles.

## Timeliness (MG, Oct 25, 2026)
- Fresh news first: send each clean story as soon as it is ready and let MG post right away; do not hold stories
  back for a schedule, and do not use stale stories just to fill a slot. Only timing rule: never two uploads
  within about an hour of each other. Content rules (what gets flagged) matter more than timing.

## Daily TikTok schedule (agreed with MG Oct 25, 2026)
MG posts 5 TikToks a day by hand at 6:00 AM, 10:00 AM, 2:00 PM, 6:00 PM and 11:00 PM ET. The scheduled task
"TikTok prep for MG" runs about 30 minutes before each slot, picks the freshest clean story, renders the video
into media/tiktok/, logs it in tiktok_posted.json and sends MG a push notification with the video link and caption.
- 6 PM slot = Amharic. All others English (switch if the day's freshest story clearly suits the other language).
- Hot news is NOT skipped. Cover it with careful language (below) instead.

### Careful language for hot news (TikTok only; Facebook keeps its own rules)
- Slide 1 title and the first line of the caption: no "war", "killed", "dead", "massacre", "attack", "drone strike",
  "bomb", "fighting", "clashes". Use neutral framing: "What we know about...", "Tensions in...", "Thousands
  displaced from...", "Residents report...", "Officials respond to...", "UN calls for...".
- No death or injury counts anywhere in the video or caption, and never mention harm to children. If an event
  involved deaths, say it once in a middle slide in plain words ("lives were reported lost"; "civilians were
  reported harmed"), with attribution, and focus the rest on displacement, aid, official reactions,
  investigations and what is still unknown.
- No graphic words (burned, bodies, blood, slaughtered), no ethnic or religious targeting language on slide 1
  (say "residents" or "farmers"; name a community only in a middle slide if the source does).
- Government-vs-government rhetoric: give each side's position in neutral reported speech; at most one short
  quote per side; never a heated quote on slide 1.
- No migration-fraud/trafficking framing; no story told twice in two languages; no re-upload of a flagged story.
- 4-5 slides, last slide = neutral call (protect civilians, aid access, dialogue, investigations) + follow line.
