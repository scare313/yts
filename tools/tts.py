#!/usr/bin/env python3
"""
History Video Studio — narration with exact scene timings (ElevenLabs or Sarvam).

Reads the scene file(s) in a video folder, sends the narration to a voice
provider, and writes into the same folder:

  audio.mp3      the full narration
  timing.json    exact start time of every scene (the engine syncs to this)
  chapters.txt   YouTube chapter list (long videos with "chapter" fields)
  script.txt     the narration text that was sent

Usage — Sarvam (Bulbul, Indian voices)
  python tts.py VIDEO_FOLDER --provider sarvam --audition          # one sample per voice → pick a speaker
  python tts.py VIDEO_FOLDER --provider sarvam --speaker shubh      # real run
  key: environment variable SARVAM_API_KEY (or --key)

Usage — ElevenLabs
  python tts.py VIDEO_FOLDER --voice VOICE_ID                       # real run
  key: environment variable ELEVENLABS_API_KEY (or --key)

Both
  --dry-run   count characters and estimate the cost, no API call
  --mock      silent placeholder audio at speaking pace, to test timing for free

Only standard Python is needed. ffmpeg is optional but recommended (MP3 output, cleaner joins).
Re-runs are cheap: results are cached in VIDEO_FOLDER/tts_cache/. Edit one scene and
only that part is generated again.
"""
import argparse, base64, hashlib, json, os, re, shutil, subprocess, sys, time, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128"


# ------------------------------------------------------------------ scene file
def lenient_json(txt, name):
    s = txt.lstrip("﻿").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", s)
    if m:
        s = m.group(1)
    s = re.sub(r",\s*([}\]])", r"\1", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {name} is not valid JSON (line {e.lineno}, col {e.colno}): {e.msg}")


def load_spec(folder):
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".json") and "timing" not in f.lower()],
                   key=lambda s: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)])
    if not files:
        sys.exit("ERROR: no scene file (spec.json) in " + folder)
    parts = [(f, lenient_json(open(os.path.join(folder, f), encoding="utf-8").read(), f)) for f in files]
    base = next((p for p in parts if p[0].lower().startswith("spec") and "meta" in p[1]), None) or \
        next((p for p in parts if "meta" in p[1]), parts[0])
    spec = json.loads(json.dumps(base[1]))
    spec.setdefault("scenes", [])
    for name, data in parts:
        if name != base[0] and isinstance(data.get("scenes"), list):
            spec["scenes"].extend(data["scenes"])
    if not spec["scenes"]:
        sys.exit("ERROR: the scene file has no scenes.")
    return spec


# ------------------------------------------------------------------ helpers
def have(cmd):
    return shutil.which(cmd) is not None


def probe_duration(path):
    if not have("ffprobe"):
        return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except Exception:
        return None


def fmt_ts(sec):
    sec = int(round(sec))
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def make_chunks(texts, max_chars):
    chunks, cur, size = [], [], 0
    for i, t in enumerate(texts):
        add = len(t) + 2
        if cur and size + add > max_chars:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(i)
        size += add
    if cur:
        chunks.append(cur)
    return chunks


def call_api(key, voice, body, retries=4):
    req = urllib.request.Request(API.format(voice=voice), data=json.dumps(body).encode("utf-8"),
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  ElevenLabs busy ({e.code}); retrying in {wait}s…")
                time.sleep(wait)
                continue
            sys.exit(f"ERROR from ElevenLabs ({e.code}): {msg[:500]}")
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            sys.exit(f"ERROR: could not reach ElevenLabs: {e}")


def mock_chunk(text, path):
    """Silent audio of the estimated length + fake character timings (for testing pacing)."""
    if not have("ffmpeg"):
        sys.exit("ERROR: --mock needs ffmpeg installed.")
    cps = 14.0
    dur = max(1.0, len(text) / cps)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", f"{dur:.3f}", "-c:a", "libmp3lame", "-b:a", "128k", path], check=True)
    starts = [i / cps for i in range(len(text))]
    return {"characters": list(text), "character_start_times_seconds": starts,
            "character_end_times_seconds": [s + 1 / cps for s in starts]}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="Narration + exact scene timings for History Video Studio (ElevenLabs or Sarvam)")
    ap.add_argument("folder", help="video folder containing spec.json")
    ap.add_argument("--provider", choices=["elevenlabs", "sarvam"], default=os.environ.get("TTS_PROVIDER", "elevenlabs"),
                    help="voice provider (default elevenlabs, or set env TTS_PROVIDER=sarvam)")
    ap.add_argument("--voice", help="ElevenLabs voice ID (Voice Library → your voice → ID)")
    ap.add_argument("--key", help="API key (default: env ELEVENLABS_API_KEY or SARVAM_API_KEY)")
    ap.add_argument("--model", help="ElevenLabs: eleven_multilingual_v2 (default), eleven_v3 … · Sarvam: bulbul:v3 (default), bulbul:v4-flash")
    ap.add_argument("--speaker", default="shubh", help="Sarvam voice (lowercase), e.g. shubh, aditya, rahul, kabir, ritu, priya")
    ap.add_argument("--pace", type=float, default=1.0, help="Sarvam speaking pace 0.5–2.0")
    ap.add_argument("--temperature", type=float, default=0.6, help="Sarvam expressiveness 0.01–1.0 (higher = livelier, less stable)")
    ap.add_argument("--sample-rate", type=int, default=44100, help="Sarvam sample rate (44100 default)")
    ap.add_argument("--gap", type=float, default=0.3, help="Sarvam: seconds of silence between scenes")
    ap.add_argument("--dict-id", help="Sarvam pronunciation dictionary ID (fix names like सिराजुद्दौला)")
    ap.add_argument("--lang", default="hi-IN", help="Sarvam language code (hi-IN default)")
    ap.add_argument("--audition", nargs="?", const="all", help="Sarvam: make one sample per voice (all, male, female, or a comma list)")
    ap.add_argument("--audition-text", help="text for --audition (default: the first scene's narration)")
    ap.add_argument("--stability", type=float, default=0.45)
    ap.add_argument("--similarity", type=float, default=0.75)
    ap.add_argument("--style", type=float, default=0.15)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--max-chars", type=int, default=2500, help="characters per request (default 2500)")
    ap.add_argument("--dry-run", action="store_true", help="only count characters and chunks")
    ap.add_argument("--mock", action="store_true", help="silent placeholder audio, no API call (needs ffmpeg)")
    ap.add_argument("--fresh", action="store_true", help="ignore the cache and regenerate everything")
    a = ap.parse_args()
    if not a.key:
        a.key = os.environ.get("SARVAM_API_KEY" if a.provider == "sarvam" else "ELEVENLABS_API_KEY")
    if not a.model:
        a.model = "bulbul:v3" if a.provider == "sarvam" else "eleven_multilingual_v2"

    folder = os.path.abspath(a.folder)
    spec = load_spec(folder)
    scenes = spec["scenes"]
    texts = [(s.get("narration") or s.get("caption") or "").strip() for s in scenes]
    empty = [i + 1 for i, t in enumerate(texts) if not t]
    if empty:
        print(f"WARNING: scenes without narration: {empty} (they get a short pause)")
        texts = [t if t else "…" for t in texts]
    total = sum(len(t) for t in texts)
    chunks = make_chunks(texts, a.max_chars)
    nreq = len(scenes) if a.provider == "sarvam" else len(chunks)
    print(f"{spec.get('meta', {}).get('id', 'video')}: {len(scenes)} scenes · {total:,} characters · {nreq} request(s) · {a.provider}")
    if a.dry_run:
        if a.provider == "sarvam":
            rate = 30 if "v3" in a.model else 20
            print(f"Dry run — nothing sent. Sarvam {a.model}: about ₹{total / 10000 * rate:.2f} at ₹{rate} per 10,000 characters.")
        else:
            print("Dry run — nothing sent. Characters count against your ElevenLabs quota roughly 1:1.")
        return
    if a.provider == "sarvam":
        import importlib.util
        spec_ = importlib.util.spec_from_file_location("tts_sarvam", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts_sarvam.py"))
        mod = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(mod)
        mod.run(a, folder, spec, scenes, texts, sys.modules[__name__])
        return
    if not a.mock:
        if not a.key:
            sys.exit("ERROR: no API key. Set ELEVENLABS_API_KEY or pass --key.")
        if not a.voice:
            sys.exit("ERROR: pass --voice VOICE_ID.")

    cache = os.path.join(folder, "tts_cache")
    os.makedirs(cache, exist_ok=True)
    settings = {"stability": a.stability, "similarity_boost": a.similarity, "style": a.style, "use_speaker_boost": True, "speed": a.speed}
    v3 = "v3" in a.model
    chunk_files, scene_start, offset = [], [None] * len(scenes), 0.0
    scene_sent = [None] * len(scenes)

    for ci, idxs in enumerate(chunks):
        text = "\n\n".join(texts[i] for i in idxs)
        positions, p = [], 0
        for i in idxs:
            positions.append(p)
            p += len(texts[i]) + 2
        prev_t = "\n\n".join(texts[i] for i in chunks[ci - 1])[-400:] if ci > 0 else ""
        next_t = "\n\n".join(texts[i] for i in chunks[ci + 1])[:400] if ci + 1 < len(chunks) else ""
        key = hashlib.sha1(json.dumps([text, a.voice, a.model, settings, prev_t[-120:], a.mock]).encode("utf-8")).hexdigest()[:16]
        mp3, js = os.path.join(cache, f"chunk_{ci:03d}_{key}.mp3"), os.path.join(cache, f"chunk_{ci:03d}_{key}.json")

        if os.path.exists(mp3) and os.path.exists(js) and not a.fresh:
            align = json.load(open(js, encoding="utf-8"))
            print(f"  chunk {ci + 1}/{len(chunks)}: cached")
        else:
            print(f"  chunk {ci + 1}/{len(chunks)}: {len(text):,} chars → {'mock' if a.mock else 'ElevenLabs'}…")
            if a.mock:
                align = mock_chunk(text, mp3)
            else:
                body = {"text": text, "model_id": a.model, "voice_settings": settings}
                if not v3:
                    if prev_t: body["previous_text"] = prev_t
                    if next_t: body["next_text"] = next_t
                res = call_api(a.key, a.voice, body)
                open(mp3, "wb").write(base64.b64decode(res["audio_base64"]))
                align = res.get("alignment") or res.get("normalized_alignment")
                if not align:
                    sys.exit("ERROR: ElevenLabs returned no timestamps.")
            json.dump(align, open(js, "w", encoding="utf-8"), ensure_ascii=False)

        starts = align["character_start_times_seconds"]
        ends = align["character_end_times_seconds"]
        chars = align.get("characters", [])
        exact = len(chars) == len(text)
        for i, pos in zip(idxs, positions):
            if exact:
                sents, sp = [], 0
                for snt in re.split(r"(?<=[।?!…])\s+", texts[i].strip()):
                    if not snt.strip(): continue
                    q = pos + texts[i].find(snt, sp); sp = texts[i].find(snt, sp) + len(snt)
                    sents.append(round(offset + max(0.0, starts[min(q, len(starts) - 1)] - 0.08), 3))
                scene_sent[i] = sents
                q = pos
                while q < len(text) - 1 and text[q].isspace():
                    q += 1
                t0 = starts[q]
            else:  # alignment length differs (normalised text) → proportional fallback
                t0 = starts[min(len(starts) - 1, int(pos / max(1, len(text)) * len(starts)))]
            scene_start[i] = offset + max(0.0, t0 - 0.12)
        dur = probe_duration(mp3) or (ends[-1] + 0.15 if ends else 0)
        chunk_files.append(mp3)
        offset += dur

    scene_start[0] = 0.0
    for i in range(1, len(scene_start)):  # keep strictly increasing
        if scene_start[i] <= scene_start[i - 1]:
            scene_start[i] = scene_start[i - 1] + 0.5

    out_mp3 = os.path.join(folder, "audio.mp3")
    remove_old_audio(folder, "audio.mp3")
    if have("ffmpeg") and len(chunk_files) > 1:
        lst = os.path.join(cache, "concat.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for c in chunk_files:
                f.write("file '" + c.replace("\\", "/").replace("'", "'\\''") + "'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out_mp3], check=True)
    else:
        with open(out_mp3, "wb") as o:
            for c in chunk_files:
                o.write(open(c, "rb").read())
    total_dur = probe_duration(out_mp3) or offset
    write_outputs(folder, scenes, texts, scene_start, total_dur, "mock" if a.mock else "elevenlabs", a.model, a.voice, scene_sent)


def remove_old_audio(folder, keep):
    for f in os.listdir(folder):
        if re.match(r"(audio|narration|voice)\.(mp3|wav|m4a|aac|ogg)$", f, re.I) and f != keep:
            os.remove(os.path.join(folder, f))


def write_outputs(folder, scenes, texts, scene_start, total_dur, source, model, voice, sentences=None):
    timing = {"duration": round(total_dur, 3), "source": source, "model": model, "voice": voice,
              "scenes": [{"id": s.get("id", i + 1), "start": round(t, 3)} for i, (s, t) in enumerate(zip(scenes, scene_start))]}
    for i, sc in enumerate(timing["scenes"]):
        if sentences and sentences[i] and len(sentences[i]) > 1:
            sc["sentences"] = sentences[i]
    json.dump(timing, open(os.path.join(folder, "timing.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(folder, "script.txt"), "w", encoding="utf-8").write("\n\n".join(texts))

    chap, last = [], None
    for s, t in zip(scenes, scene_start):
        c = s.get("chapter")
        if c and c != last:
            chap.append((t, c))
            last = c
    if chap:
        if chap[0][0] > 0.5:
            chap.insert(0, (0.0, "शुरुआत"))
        else:
            chap[0] = (0.0, chap[0][1])
        open(os.path.join(folder, "chapters.txt"), "w", encoding="utf-8").write("\n".join(f"{fmt_ts(t)} {c}" for t, c in chap) + "\n")
        print(f"chapters.txt written ({len(chap)} chapters) — paste into the YouTube description.")
    audio = next((f for f in os.listdir(folder) if re.match(r"audio\.(mp3|wav)$", f)), "audio")
    print(f"Done: {audio} ({total_dur:.1f}s) + timing.json in {folder}")


if __name__ == "__main__":
    main()
