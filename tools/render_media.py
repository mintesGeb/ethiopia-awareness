#!/usr/bin/env python3
"""Render a daily news explainer as (1) a vertical video reel and (2) a square-ish graphic card.

usage: python3 tools/render_media.py <spec.json> <out_dir> [--card-only]
outputs: <out_dir>/<id>.mp4 (1080x1920, ~25-35s, soft synthesized pad audio)
         <out_dir>/<id>_card.jpg (1080x1350, < 1 MB)

spec.json:
{
  "id": "2026-10-13_food",                 # file stem
  "lang": "en" | "am",                     # am = Amharic (Ethiopic font)
  "brand": "Be-Aware",                     # page name shown small at the top (optional)
  "kicker": "FOOD SECURITY · TIGRAY & OROMIA",
  "slides": [                               # 4-6 slides; first = hook, last = call to action
    {"title": "Hunger is rising behind the headlines", "body": "optional smaller text"},
    {"stat": "40%+", "body": "estimated crop losses in East & West Hararghe"},
    ...
  ],
  "source": "Source: Addis Standard / FEWS NET, Oct 9, 2026",
  "card": {"stat": "IPC 3", "title": "...", "body": "..."}   # optional; defaults to first stat slide
}
Text only, no photos (news photos are copyrighted). Neutral palette: no flags or party colours.
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
W, H, FPS = 1080, 1920, 24
BG_TOP, BG_BOT = np.array([14, 20, 30], np.float32), np.array([30, 38, 52], np.float32)
ACCENT = (242, 169, 59)      # amber
INK = (244, 241, 234)
MUTED = (168, 176, 190)
# Facebook Reels safe zones (1080x1920), checked against a real upload on Oct 13, 2026
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, PB_Y = 400, 420, 170, 300
CTA_Y = 1690   # level with Facebook's page name + Follow button on phones
TT_CTA_Y = 1110  # TikTok: level with the profile picture (+ follow) in the right-hand column


def font(lang, weight, size):
    if lang == "am":
        f = ImageFont.truetype(os.path.join(FD, "NotoSansEthiopic.ttf"), size)
        f.set_variation_by_name({"bold": "Bold", "semi": "SemiBold", "reg": "Regular", "black": "ExtraBold"}[weight])
        return f
    name = {"bold": "Inter-Bold.otf", "semi": "Inter-SemiBold.otf", "reg": "Inter-Regular.otf", "black": "Inter-ExtraBold.otf"}[weight]
    for d in (FD, "/usr/share/fonts/opentype/inter"):
        if os.path.exists(os.path.join(d, name)):
            return ImageFont.truetype(os.path.join(d, name), size)
    dv = "DejaVuSans.ttf" if weight == "reg" else "DejaVuSans-Bold.ttf"
    return ImageFont.truetype(os.path.join("/usr/share/fonts/truetype/dejavu", dv), size)


def wrap(draw, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit(draw, text, lang, weight, size, maxw, maxh, lh=1.22, minsize=34):
    while True:
        f = font(lang, weight, size)
        lines = wrap(draw, text, f, maxw)
        h = int(len(lines) * size * lh)
        too_wide = any(draw.textlength(ln, font=f) > maxw for ln in lines)   # e.g. a long number can't wrap
        if (h <= maxh and not too_wide) or size <= minsize:
            return f, lines, size, h
        size -= 4


def background(w, h):
    y = np.linspace(0, 1, h)[:, None, None]
    g = BG_TOP + (BG_BOT - BG_TOP) * y
    img = np.repeat(g, w, axis=1)
    yy, xx = np.mgrid[0:h, 0:w]
    glow = np.clip(1 - np.hypot(xx - w * 0.85, yy - h * 0.12) / (w * 0.9), 0, 1) ** 2
    img = img + glow[:, :, None] * np.array([60, 40, 10], np.float32) * 0.5
    return img.astype(np.float32)


# --- Slide-1 locator map (approved by MG Oct 14, 2026) -------------------------
# Outline: Ethiopia's outer border only (no internal region lines, some are disputed),
# from github.com/johan/world.geo.json (Unlicense / Natural Earth, public domain).
# Spec field "places": list of keys from PLACES (max 2 shown), e.g. ["mekelle"];
# [] = nationwide story (outline, no dot). Optional "place_label" overrides the label.
PLACES = {  # key: (lat, lon, English label, Amharic label)
    "tigray": (13.9, 39.0, "TIGRAY", "ትግራይ"), "mekelle": (13.50, 39.47, "MEKELLE, TIGRAY", "መቐለ፣ ትግራይ"),
    "adwa": (14.16, 38.90, "ADWA, TIGRAY", "አድዋ፣ ትግራይ"), "shire": (14.10, 38.28, "SHIRE, TIGRAY", "ሽሬ፣ ትግራይ"),
    "alamata": (12.42, 39.55, "ALAMATA", "አላማጣ"), "korem": (12.51, 39.52, "KOREM", "ኮረም"),
    "zalambessa": (14.52, 39.38, "ZALAMBESSA, TIGRAY", "ዛላምበሳ፣ ትግራይ"), "humera": (14.29, 36.62, "HUMERA", "ሁመራ"),
    "amhara": (11.5, 38.0, "AMHARA", "አማራ"), "gondar": (12.61, 37.47, "GONDAR, AMHARA", "ጎንደር፣ አማራ"),
    "bahir_dar": (11.59, 37.39, "BAHIR DAR, AMHARA", "ባሕር ዳር፣ አማራ"), "dessie": (11.13, 39.63, "DESSIE, AMHARA", "ደሴ፣ አማራ"),
    "afar": (11.8, 41.0, "AFAR", "አፋር"), "semera": (11.79, 41.01, "SEMERA, AFAR", "ሰመራ፣ አፋር"),
    "oromia": (7.8, 39.0, "OROMIA", "ኦሮሚያ"), "east_hararghe": (9.0, 41.8, "EAST HARARGHE, OROMIA", "ምሥራቅ ሐረርጌ፣ ኦሮሚያ"),
    "west_hararghe": (8.9, 40.7, "WEST HARARGHE, OROMIA", "ምዕራብ ሐረርጌ፣ ኦሮሚያ"), "borana": (4.5, 38.5, "BORANA, OROMIA", "ቦረና፣ ኦሮሚያ"),
    "jimma": (7.67, 36.83, "JIMMA, OROMIA", "ጅማ፣ ኦሮሚያ"), "nekemte": (9.09, 36.55, "NEKEMTE, OROMIA", "ነቀምት፣ ኦሮሚያ"),
    "addis_ababa": (9.03, 38.74, "ADDIS ABABA", "አዲስ አበባ"), "dire_dawa": (9.60, 41.86, "DIRE DAWA", "ድሬዳዋ"),
    "harar": (9.31, 42.12, "HARAR", "ሐረር"), "somali": (7.0, 43.5, "SOMALI REGION", "ሶማሌ ክልል"),
    "benishangul": (10.8, 35.5, "BENISHANGUL-GUMUZ", "ቤኒሻንጉል ጉሙዝ"), "gambela": (7.9, 34.6, "GAMBELA", "ጋምቤላ"),
    "sidama": (6.7, 38.5, "SIDAMA", "ሲዳማ"), "gurage": (8.12, 38.37, "EAST GURAGE, CENTRAL ETH.", "ምሥራቅ ጉራጌ"), "south": (6.2, 37.4, "SOUTHERN ETHIOPIA", "ደቡብ ኢትዮጵያ"),
    "southwest": (7.27, 36.24, "SOUTHWEST ETHIOPIA", "ደቡብ ምዕራብ ኢትዮጵያ"),
}
_RING = None


def draw_locator(d, spec, x, y, w):
    """Draw the Ethiopia outline + place dot(s) + label. Returns the height used."""
    global _RING
    if _RING is None:
        with open(os.path.join(HERE, "ethiopia_outline.geo.json"), encoding="utf-8") as fh:
            _RING = json.load(fh)["features"][0]["geometry"]["coordinates"][0]
    lang = spec.get("lang", "en")
    lons = [p[0] for p in _RING]; lats = [p[1] for p in _RING]
    lo0, lo1, la0, la1 = min(lons), max(lons), min(lats), max(lats)
    k = math.cos(math.radians(9)); s = w / ((lo1 - lo0) * k); mh = (la1 - la0) * s
    P = lambda lo, la: (x + (lo - lo0) * k * s, y + (la1 - la) * s)
    pts = [P(*p) for p in _RING]
    d.polygon(pts, fill=(40, 50, 66, 255))
    d.line(pts + [pts[0]], fill=(120, 130, 146, 255), width=3, joint="curve")
    keys = [p for p in spec.get("places", []) if p in PLACES][:2]
    for key in keys:
        cx, cy = P(PLACES[key][1], PLACES[key][0])
        d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=ACCENT + (110,), width=4)
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=ACCENT + (255,))
    label = spec.get("place_label")
    if not label:
        names = [PLACES[k_][3 if lang == "am" else 2] for k_ in keys]
        label = (" እና " if lang == "am" else " & ").join(names) if names else ("ኢትዮጵያ" if lang == "am" else "ETHIOPIA")
    d.text((x, y + mh + 22), label, font=font(lang, "bold", 30), fill=ACCENT + (255,))
    return int(mh + 70)


def text_layer(slide, spec, w, h, idx, total, card=False):
    """Transparent RGBA layer with all text for one slide."""
    lang = spec.get("lang", "en")
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    mx = 90
    # Reels: keep clear of Facebook's overlays (status bar/back+search icons on top,
    # page name + caption at the bottom, like/comment/share column on the right).
    maxw = w - 2 * mx if card else w - mx - SAFE_RIGHT
    top = SAFE_TOP if not card else 90
    # brand + kicker
    if spec.get("brand"):
        # Channel name in white; MG's signature ("MG") smaller, in the amber accent.
        name, sig = spec["brand"].strip(), ""
        if name.upper().endswith(" MG"):
            name, sig = name[:-3].strip(), "MG"
        nf = font("en", "bold", 32)
        by = top - 72
        d.text((mx, by), name.upper(), font=nf, fill=INK)
        if sig:
            sf_ = font("en", "bold", 21)
            nx = mx + d.textlength(name.upper(), font=nf) + 12
            # align baselines
            yb = by + nf.getmetrics()[0] - sf_.getmetrics()[0]
            d.text((nx, yb), sig, font=sf_, fill=ACCENT)
    kf = font(lang, "bold", 34)
    d.rectangle([mx, top, mx + 64, top + 8], fill=ACCENT)
    d.text((mx, top + 26), spec.get("kicker", ""), font=kf, fill=ACCENT)
    # main block, vertically centred in the middle zone
    zone_top, zone_bot = (top + 120, h - SAFE_BOTTOM - 200) if not card else (top + 110, h - 210)
    tiktok = spec.get("platform") == "tiktok"
    if tiktok and not card and idx == total - 1:
        zone_bot = min(zone_bot, TT_CTA_Y - 120)
    if not card and idx == 0 and "places" in spec:
        zone_top += draw_locator(d, spec, mx, top + 120, 330) + 30
    blocks = []
    if slide.get("stat"):
        f, lines, s, bh = fit(d, slide["stat"], "en" if slide["stat"].isascii() else lang, "black", 210, maxw, 240)
        blocks.append((f, lines, s, bh, ACCENT, 1.05))
    if slide.get("title"):
        f, lines, s, bh = fit(d, slide["title"], lang, "bold", 96 if not slide.get("stat") else 70, maxw, 420 if not card else 560)
        blocks.append((f, lines, s, bh, INK, 1.2))
    if slide.get("body"):
        used = sum(int(len(b[1]) * b[2] * b[5]) for b in blocks) + 44 * len(blocks)
        room = max(120, zone_bot - zone_top - used)   # body gets whatever space is left, so nothing overflows
        f, lines, s, bh = fit(d, slide["body"], lang, "reg", 58, maxw, min(room, 680), lh=1.3, minsize=32)
        blocks.append((f, lines, s, bh, INK if not slide.get("title") else MUTED, 1.3))
    gap = 44
    total_h = sum(int(len(b[1]) * b[2] * b[5]) for b in blocks) + gap * (len(blocks) - 1)
    y = zone_top + max(0, (zone_bot - zone_top - total_h) // 2)
    for f, lines, s, bh, col, lh in blocks:
        for ln in lines:
            d.text((mx, y), ln, font=f, fill=col)
            y += int(s * lh)
        y += gap
    # Reels, last slide only: a small "Follow for more" arrow pointing left at Facebook's
    # Follow button (approved by MG Oct 14, 2026). Kept well right of "Follow" so the
    # arrowhead stays clear when the button changes to "Following".
    if not card and idx == total - 1 and tiktok:
        # TikTok: the follow "+" sits on the profile picture in the right-hand column
        y = TT_CTA_Y
        tail, tip = 690, 905
        d.line([(tail, y), (tip - 18, y)], fill=ACCENT, width=7)
        d.polygon([(tip, y), (tip - 28, y - 17), (tip - 28, y + 17)], fill=ACCENT)
        top_t, bot_t = ("ለተጨማሪ", "ይከተሉን") if lang == "am" else ("Follow", "for more")
        cf = font(lang, "bold", 27)
        cx = tail + 62
        for txt, ty in ((top_t, y - 50), (bot_t, y + 20)):
            d.text((cx - d.textlength(txt, font=cf) / 2, ty), txt, font=cf, fill=ACCENT)
    elif not card and idx == total - 1:
        y = CTA_Y
        tip, tail = 625, 835
        d.line([(tip + 18, y), (tail, y)], fill=ACCENT, width=7)
        d.polygon([(tip, y), (tip + 28, y - 17), (tip + 28, y + 17)], fill=ACCENT)
        top_t, bot_t = ("ለተጨማሪ", "ይከተሉን") if lang == "am" else ("Follow", "for more")
        cf = font(lang, "bold", 27)
        cx = tail - 62
        for txt, ty in ((top_t, y - 50), (bot_t, y + 20)):
            d.text((cx - d.textlength(txt, font=cf) / 2, ty), txt, font=cf, fill=ACCENT)
    # footer: source
    sf = font(lang if not spec.get("source", "").isascii() else "en", "reg", 30)
    slines = wrap(d, spec.get("source", ""), sf, maxw)
    fy = h - (SAFE_BOTTOM + 40 if not card else 110) - 40 * (len(slines) - 1)
    d.line([mx, fy - 28, w - mx, fy - 28], fill=(80, 90, 106), width=2)
    for ln in slines:
        d.text((mx, fy), ln, font=sf, fill=MUTED)
        fy += 40
    return np.array(L, np.float32)


def pad_audio(path, dur, sr=44100, seed=""):
    """Original, copyright-free music bed "C6", chosen by MG on Oct 14, 2026: clean 3-note chords
    (D minor -> C, open voicing, no detune), a soft bass drum about every 2.8 s (pitched so phone
    speakers can hear it) and a light shaker / rim tick. No melody. The key moves by up to two
    semitones per reel (picked from the spec id) so consecutive reels don't sound identical."""
    n = int(sr * dur); t = np.arange(n) / sr
    rng = np.random.default_rng(5)
    shift = 2 ** ([0, -2, 2][sum(map(ord, seed)) % 3] / 12)
    chords = [[146.83, 220.00, 349.23], [130.81, 196.00, 329.63]]

    def chord(freqs, length):
        tt = np.arange(int(sr * length)) / sr
        s = sum((np.sin(2 * math.pi * f * shift * tt) + 0.18 * np.sin(4 * math.pi * f * shift * tt)) * (1.0 if i == 0 else 0.8)
                for i, f in enumerate(freqs))
        return s / np.max(np.abs(s))

    sig = np.zeros(n); seg = 7.0; x = 0; i = 0
    while x < n:
        c = chord(chords[i % 2], seg + 1.5); m = min(len(c), n - x); k = np.arange(m)
        sig[x:x + m] += c[:m] * np.minimum(1, k / (sr * 1.5)) * np.minimum(1, (m - k) / (sr * 1.5))
        x += int(sr * seg); i += 1
    a = math.exp(-2 * math.pi * 2500 / sr)                      # gentle low-pass, softens the top end
    sig = np.convolve(sig, (1 - a) * a ** np.arange(80))[:n]
    sig = sig / np.max(np.abs(sig)) * 0.55

    def put(snd, at, g):
        j = int(at * sr); m = min(len(snd), n - j)
        if m > 0:
            sig[j:j + m] += snd[:m] * g

    tk = np.arange(int(sr * 0.45)) / sr
    ph = np.cumsum(60 + 60 * np.exp(-tk * 25)) / sr
    kick = (np.sin(2 * math.pi * ph) * np.exp(-tk * 9) + 0.35 * np.sin(4 * math.pi * ph) * np.exp(-tk * 14)
            + rng.standard_normal(len(tk)) * np.exp(-tk * 400) * 0.25)
    ts = np.arange(int(sr * 0.09)) / sr
    nz = rng.standard_normal(len(ts)); nz = nz - np.convolve(nz, np.ones(6) / 6, "same")
    shaker = nz * np.minimum(1, ts / 0.01) * np.exp(-ts * 45)
    tr = np.arange(int(sr * 0.06)) / sr
    rim = (np.sin(2 * math.pi * 1700 * tr) + 0.5 * np.sin(2 * math.pi * 2900 * tr)) * np.exp(-tr * 90)
    beat, b, k = 1.4, 0.0, 0
    while b < dur:
        if k % 2 == 0:
            put(kick, b, 0.5)
        put(shaker, b + beat / 2, 0.10); put(shaker, b + beat * 0.25, 0.05); put(shaker, b + beat * 0.75, 0.05)
        if k % 4 == 3:
            put(rim, b, 0.12)
        b += beat; k += 1
    sig /= np.max(np.abs(sig))
    env = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    sig = (sig * env * 0.30 * 32767).astype(np.int16)
    with wave.open(path, "wb") as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(sr); wv.writeframes(sig.tobytes())


def render_video(spec, out_dir):
    slides = spec["slides"]
    n = len(slides)
    durs = []
    for s in slides:
        words = len((s.get("title", "") + " " + s.get("body", "") + " " + s.get("stat", "")).split())
        if spec.get("platform") == "tiktok":
            durs.append(min(4.6, max(2.8, 1.2 + words * 0.21)))     # TikTok: quicker pacing
        else:
            durs.append(min(6.0, max(3.5, 1.6 + words * 0.26)))
    total = sum(durs)
    bg = background(W + 120, H)
    layers = [text_layer(s, spec, W, H, i, n) for i, s in enumerate(slides)]
    vid_tmp = os.path.join(out_dir, spec["id"] + "_silent.mp4")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "21", "-pix_fmt", "yuv420p", vid_tmp], stdin=subprocess.PIPE)
    t0 = 0.0
    fade = 0.45
    for i, (lay, dur) in enumerate(zip(layers, durs)):
        nf = int(dur * FPS)
        a = lay[:, :, 3:4] / 255.0
        rgb = lay[:, :, :3]
        for k in range(nf):
            t = k / FPS
            gt = (t0 + t) / total
            off = int(60 + 60 * math.sin(gt * math.pi))          # slow background drift
            frame = bg[:, off:off + W].copy()
            # Slide 1 is fully visible from the first frame, because Facebook uses
            # the first frame as the reel's thumbnail (a fade-in left it blank).
            fade_in = 1.0 if i == 0 else t / fade
            alpha = min(1.0, fade_in, (dur - t) / fade) if i < n - 1 else min(1.0, fade_in)
            rise = 0 if i == 0 else int((1 - min(1.0, t / 0.6)) ** 3 * 40)   # text eases up into place
            if rise:
                aa = np.zeros_like(a); cc = np.zeros_like(rgb)
                aa[:-rise] = a[rise:]; cc[:-rise] = rgb[rise:]
            else:
                aa, cc = a, rgb
            frame = frame * (1 - aa * alpha) + cc * aa * alpha
            # progress segments (story style)
            seg_w = (W - 2 * 60 - (n - 1) * 10) / n
            for j in range(n):
                x0 = int(60 + j * (seg_w + 10)); x1 = int(x0 + seg_w)
                frame[PB_Y:PB_Y + 6, x0:x1] = (70, 78, 92)
                fill = 1.0 if j < i else (t / dur if j == i else 0)
                if fill > 0:
                    frame[PB_Y:PB_Y + 6, x0:x0 + int((x1 - x0) * fill)] = ACCENT
            p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
        t0 += dur
    p.stdin.close(); p.wait()
    wav = os.path.join(out_dir, spec["id"] + "_pad.wav")
    pad_audio(wav, total, seed=spec.get("id", ""))
    out = os.path.join(out_dir, spec["id"] + ".mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", vid_tmp, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(vid_tmp); os.remove(wav)
    return out, total


def render_card(spec, out_dir):
    cw, ch = 1080, 1350
    card = spec.get("card") or next((s for s in spec["slides"] if s.get("stat")), spec["slides"][0])
    bg = background(cw, ch)
    lay = text_layer(card, spec, cw, ch, 0, 1, card=True)
    a = lay[:, :, 3:4] / 255.0
    img = bg * (1 - a) + lay[:, :, :3] * a
    out = os.path.join(out_dir, spec["id"] + "_card.jpg")
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out, quality=90)
    return out


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    if not spec.get("brand"):
        bf = os.path.join(HERE, "..", "BRAND.txt")
        spec["brand"] = open(bf, encoding="utf-8").read().strip() if os.path.exists(bf) else "Be-Aware MG"
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    if "--card-only" not in sys.argv:
        v, dur = render_video(spec, out_dir)
        res.update(video=v, seconds=round(dur, 1))
    res["card"] = render_card(spec, out_dir)
    print(json.dumps(res))
