"""
Sarvam (Bulbul) provider for tts.py — called as:  python tts.py FOLDER --provider sarvam ...

Sarvam returns no word timings, so every scene is voiced separately and the
exact length of each clip gives the scene timings. Clips are joined with a short
pause (--gap) into audio.mp3 (or audio.wav when ffmpeg isn't installed).
"""
import base64, hashlib, json, math, os, struct, subprocess, sys, time, urllib.error, urllib.request

API_URL = os.environ.get("SARVAM_API_URL", "https://api.sarvam.ai/text-to-speech")
MAX_CHARS = {"bulbul:v2": 1500}
VOICES_MALE = ["shubh", "aditya", "rahul", "rohan", "amit", "dev", "ratan", "varun", "manan", "sumit", "kabir", "aayan", "ashutosh",
               "advait", "anand", "tarun", "sunny", "mani", "gokul", "vijay", "mohit", "rehan", "soham"]
VOICES_FEMALE = ["ritu", "priya", "neha", "pooja", "simran", "kavya", "ishita", "shreya", "roopa", "tanya", "shruti", "suhani", "kavitha", "rupali"]


# ------------------------------------------------------------------ WAV helpers (no ffmpeg needed)
def parse_wav(data):
    """Return (channels, rate, sampwidth, pcm_bytes). Tolerates streamed headers with bogus sizes."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("not a WAV file")
    pos, fmt, pcm = 12, None, None
    while pos + 8 <= len(data):
        cid, size = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = pos + 8
        if cid == b"fmt ":
            _, ch, rate, _, _, bits = struct.unpack("<HHIIHH", data[body:body + 16])
            fmt = (ch, rate, bits // 8)
        elif cid == b"data":
            end = len(data) if size in (0, 0xFFFFFFFF) or body + size > len(data) else body + size
            pcm = data[body:end]
            break
        pos = body + size + (size & 1)
    if not fmt or pcm is None:
        raise ValueError("WAV without fmt/data chunk")
    ch, rate, sw = fmt
    pcm = pcm[: len(pcm) - (len(pcm) % (ch * sw))]
    return ch, rate, sw, pcm


def write_wav(path, ch, rate, sw, pcm):
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, ch, rate, rate * ch * sw, ch * sw, sw * 8))
        f.write(b"data" + struct.pack("<I", len(pcm)) + pcm)


def silent_wav(seconds, rate=44100):
    pcm = b"\x00\x00" * int(seconds * rate)
    out = bytearray(b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE")
    out += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16) + b"data" + struct.pack("<I", len(pcm)) + pcm
    return bytes(out)


def sentence_starts(text, pcm, ch, rate, sw):
    """Find where each sentence starts inside one scene clip, using the pauses between sentences."""
    import re as _re
    sents = [s for s in _re.split(r"(?<=[।?!…])\s+", text.strip()) if s.strip()]
    if len(sents) < 2 or sw != 2:
        return [0.0]
    n = len(pcm) // (2 * ch); hop = int(rate * 0.01)
    samples = struct.unpack("<%dh" % (n * ch), pcm[: n * ch * 2])[::ch]
    rms = [math.sqrt(sum(x * x for x in samples[i:i + hop]) / hop) for i in range(0, n - hop, hop)]
    if not rms:
        return [0.0]
    thr = max(rms) * 0.06
    gaps, i = [], 0
    while i < len(rms):
        if rms[i] < thr:
            j = i
            while j < len(rms) and rms[j] < thr: j += 1
            if (j - i) * 0.01 >= 0.11 and i > 5 and j < len(rms) - 5: gaps.append(((i + j) / 2 * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    total = n / rate; L = [len(s) for s in sents]; T = sum(L); out = [0.0]; acc = 0; used = set()
    for k in range(len(sents) - 1):
        acc += L[k]; want = total * acc / T
        best = min((g for g in range(len(gaps)) if g not in used), key=lambda g: abs(gaps[g][0] - want), default=None)
        if best is not None and abs(gaps[best][0] - want) < total * 0.25:
            used.add(best); out.append(max(out[-1] + 0.2, gaps[best][1] - 0.05))
        else:
            out.append(max(out[-1] + 0.2, want))
    return out


# ------------------------------------------------------------------ API
_PREF = {"old_field": False}


def call(key, body, retries=5):
    variants = [body, {**{k: v for k, v in body.items() if k != "language_code"}, "target_language_code": body["language_code"]}]
    if _PREF["old_field"]:
        variants = variants[1:]
    last = ""
    for v in variants:
        for attempt in range(retries):
            req = urllib.request.Request(API_URL, data=json.dumps(v).encode("utf-8"),
                                         headers={"api-subscription-key": key, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    res = json.loads(r.read().decode("utf-8"))
                    _PREF["old_field"] = "target_language_code" in v
                    audios = res.get("audios") or []
                    if not audios:
                        sys.exit(f"ERROR: Sarvam returned no audio: {str(res)[:300]}")
                    return base64.b64decode(audios[0])
            except urllib.error.HTTPError as e:
                last = e.read().decode("utf-8", "replace")
                if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                    wait = 3 * (attempt + 1)
                    print(f"    Sarvam busy ({e.code}); retrying in {wait}s…")
                    time.sleep(wait)
                    continue
                if e.code in (400, 422) and v is variants[0] and "language" in last.lower():
                    break  # try the older field name
                if e.code in (401, 403):
                    sys.exit("ERROR: Sarvam rejected the API key (check SARVAM_API_KEY and that you have credits).")
                sys.exit(f"ERROR from Sarvam ({e.code}): {last[:500]}")
            except urllib.error.URLError as e:
                if attempt < retries - 1:
                    time.sleep(3)
                    continue
                sys.exit(f"ERROR: could not reach Sarvam: {e}")
    sys.exit(f"ERROR from Sarvam: {last[:500]}")


def body_for(a, text, speaker):
    b = {"text": text, "language_code": a.lang, "model": a.model, "speaker": speaker, "pace": a.pace,
         "speech_sample_rate": a.sample_rate, "output_audio_codec": "wav"}
    if a.model != "bulbul:v2":
        b["temperature"] = a.temperature
    if a.dict_id:
        b["dict_id"] = a.dict_id
    return b


def split_text(text, limit):
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for sent in [s for s in text.replace("।", "।\n").replace("?", "?\n").replace("!", "!\n").split("\n") if s.strip()]:
        if len(cur) + len(sent) + 1 > limit and cur:
            parts.append(cur.strip())
            cur = ""
        cur += " " + sent
    if cur.strip():
        parts.append(cur.strip())
    return parts


# ------------------------------------------------------------------ audition
def audition(a, folder, texts):
    sel = a.audition.lower()
    voices = VOICES_MALE + VOICES_FEMALE if sel == "all" else VOICES_MALE if sel == "male" else VOICES_FEMALE if sel == "female" \
        else [v.strip().lower() for v in sel.split(",") if v.strip()]
    text = (a.audition_text or texts[0])[:400]
    out = os.path.join(folder, "voice_samples")
    os.makedirs(out, exist_ok=True)
    cost = len(text) * len(voices) / 10000 * (30 if "v3" in a.model else 20)
    print(f"Audition: {len(voices)} voices × {len(text)} characters ≈ ₹{cost:.2f}")
    if not a.key and not a.mock:
        sys.exit("ERROR: no API key. Set SARVAM_API_KEY or pass --key.")
    for v in voices:
        wav = silent_wav(len(text) / 14) if a.mock else call(a.key, body_for(a, text, v))
        path = os.path.join(out, f"{v}.wav")
        open(path, "wb").write(wav)
        print(f"  {v}.wav")
    print(f"Listen to the files in {out} and pass your favourite with --speaker NAME.")


# ------------------------------------------------------------------ main run
def run(a, folder, spec, scenes, texts, core):
    if a.audition:
        return audition(a, folder, texts)
    if not a.mock and not a.key:
        sys.exit("ERROR: no API key. Set SARVAM_API_KEY or pass --key.")
    limit = MAX_CHARS.get(a.model, 2500)
    cache = os.path.join(folder, "tts_cache")
    os.makedirs(cache, exist_ok=True)
    fmt, pcm_parts, starts, t = None, [], [], 0.0
    sentences = []
    spent = 0
    for i, text in enumerate(texts):
        clip_pcm = b""
        for j, piece in enumerate(split_text(text, limit)):
            key = hashlib.sha1(json.dumps([piece, a.speaker, a.model, a.pace, a.temperature, a.sample_rate, a.lang, a.dict_id, a.mock],
                                          ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
            path = os.path.join(cache, f"sarvam_{i + 1:03d}_{j}_{key}.wav")
            if os.path.exists(path) and not a.fresh:
                data = open(path, "rb").read()
                tag = "cached"
            else:
                data = silent_wav(max(0.8, len(piece) / 14), a.sample_rate) if a.mock else call(a.key, body_for(a, piece, a.speaker))
                open(path, "wb").write(data)
                spent += len(piece)
                tag = "mock" if a.mock else f"{len(piece)} chars"
                time.sleep(0 if a.mock else 0.15)
            ch, rate, sw, pcm = parse_wav(data)
            if fmt is None:
                fmt = (ch, rate, sw)
            elif (ch, rate, sw) != fmt:
                sys.exit(f"ERROR: scene {i + 1} audio format differs ({ch}ch {rate}Hz) — run again with --fresh.")
            clip_pcm += pcm
            print(f"  scene {i + 1}/{len(texts)}{'' if j == 0 else f' part {j + 1}'}: {tag}")
        ch, rate, sw = fmt
        dur = len(clip_pcm) / (ch * rate * sw)
        starts.append(max(0.0, t - (0.1 if i else 0)))
        sent_rel = sentence_starts(text, clip_pcm, ch, rate, sw)
        sentences.append([round(t + x, 3) for x in sent_rel] if len(sent_rel) > 1 else None)
        gap = b"\x00" * (int(a.gap * rate) * ch * sw) if i < len(texts) - 1 else b"\x00" * (int(0.4 * rate) * ch * sw)
        pcm_parts.append(clip_pcm + gap)
        t += dur + len(gap) / (ch * rate * sw)
    ch, rate, sw = fmt
    pcm = b"".join(pcm_parts)
    total = len(pcm) / (ch * rate * sw)
    wav_path = os.path.join(folder, "audio.wav")
    write_wav(wav_path, ch, rate, sw, pcm)
    keep = "audio.wav"
    if core.have("ffmpeg"):
        mp3 = os.path.join(folder, "audio.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path, "-c:a", "libmp3lame", "-b:a", "192k", mp3], check=True)
        os.remove(wav_path)
        keep = "audio.mp3"
    core.remove_old_audio(folder, keep)
    starts[0] = 0.0
    if spent:
        print(f"Characters sent this run: {spent:,} (≈ ₹{spent / 10000 * (30 if 'v3' in a.model else 20):.2f})")
    core.write_outputs(folder, scenes, texts, starts, total, "mock" if a.mock else "sarvam", a.model, a.speaker, sentences)
