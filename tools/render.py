#!/usr/bin/env python3
"""
History Video Studio — frame-perfect MP4 render.

Opens studio_engine.html in a hidden Chrome, draws every frame of the video in
the folder, encodes it with ffmpeg and adds the narration (and music, if any).
Your laptop's speed only changes how long it takes, never the quality.

Setup (once)
  pip install playwright
  (uses your installed Google Chrome or Edge; if you have neither: python -m playwright install chromium)
  install ffmpeg and make sure `ffmpeg` works in a terminal

Usage
  python render.py VIDEO_FOLDER                     # → VIDEO_FOLDER/<id>.mp4 + <id>_thumbnail.png
  python render.py VIDEO_FOLDER --from 30 --to 45   # preview a section (seconds)
  python render.py VIDEO_FOLDER --fps 24            # faster render
  python render.py VIDEO_FOLDER --headed            # use a visible window (often faster: real GPU)
"""
import argparse, asyncio, base64, json, mimetypes, os, re, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


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


def load_folder(folder):
    names = os.listdir(folder)
    nat = lambda s: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]
    jsons = sorted([f for f in names if f.lower().endswith(".json") and "timing" not in f.lower()], key=nat)
    if not jsons:
        sys.exit("ERROR: no spec.json in " + folder)
    parts = [(f, lenient_json(open(os.path.join(folder, f), encoding="utf-8").read(), f)) for f in jsons]
    base = next((p for p in parts if p[0].lower().startswith("spec") and "meta" in p[1]), None) or next((p for p in parts if "meta" in p[1]), parts[0])
    spec = json.loads(json.dumps(base[1]))
    spec.setdefault("scenes", [])
    spec.setdefault("characters", {})
    for n, d in parts:
        if n != base[0]:
            spec["scenes"].extend(d.get("scenes", []))
            spec["characters"].update(d.get("characters", {}))
    timing = None
    tf = next((f for f in names if f.lower().endswith(".json") and "timing" in f.lower()), None)
    if tf:
        timing = lenient_json(open(os.path.join(folder, tf), encoding="utf-8").read(), tf)
    sfx = {}
    for f in names:
        m = re.match(r"sfx_([a-z_]+)\.(mp3|wav|ogg|m4a)$", f, re.I)
        if m:
            sfx[m.group(1).lower()] = f"data:{mimetypes.guess_type(f)[0] or 'audio/mpeg'};base64," + base64.b64encode(open(os.path.join(folder, f), "rb").read()).decode()
    audio = [f for f in names if re.search(r"\.(mp3|wav|m4a|aac|ogg)$", f, re.I) and not f.lower().startswith("sfx_")]
    music = next((f for f in audio if f.lower().startswith("music")), None)
    narr = next((f for f in audio if f != music and re.match(r"(audio|narration|voice)", f, re.I)), None) or next((f for f in audio if f != music), None)
    images = {}
    for f in names:
        if re.search(r"\.(png|jpe?g|webp)$", f, re.I) and "thumbnail" not in f.lower():
            mt = mimetypes.guess_type(f)[0] or "image/png"
            images[f] = f"data:{mt};base64," + base64.b64encode(open(os.path.join(folder, f), "rb").read()).decode()
    return spec, timing, narr, music, images, sfx


def duration_of(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
        return float(out.strip())
    except Exception:
        return 0.0


async def run(a):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("ERROR: run  pip install playwright  and  python -m playwright install chromium")
    if not shutil.which("ffmpeg"):
        sys.exit("ERROR: ffmpeg not found. Install it and make sure `ffmpeg -version` works.")
    folder = os.path.abspath(a.folder)
    spec, timing, narr, music, images, sfx = load_folder(folder)
    engine = os.path.abspath(a.engine or next((p for p in [os.path.join(HERE, "studio_engine.html"), os.path.join(HERE, "..", "studio_engine.html")] if os.path.exists(p)), ""))
    if not os.path.exists(engine):
        sys.exit("ERROR: studio_engine.html not found — pass --engine PATH")
    narr_dur = duration_of(os.path.join(folder, narr)) if narr else 0.0
    vid = re.sub(r"[^\w\-]+", "_", spec.get("meta", {}).get("id") or "video")
    out = os.path.abspath(a.out or os.path.join(folder, vid + (".mp4" if a.start is None and a.end is None else "_preview.mp4")))

    async with async_playwright() as p:
        args = ["--ignore-gpu-blocklist", "--enable-gpu-rasterization"]
        if a.gl == "swiftshader":
            args += ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
        browser = None
        for ch in ([a.browser] if a.browser != "auto" else ["chrome", "msedge", "chromium"]):
            try:
                kw = {} if ch == "chromium" else {"channel": ch}
                browser = await p.chromium.launch(headless=not a.headed, args=args, **kw)
                print(f"  browser: {ch}")
                break
            except Exception as e:
                last = e
        if browser is None:
            sys.exit(f"ERROR: could not start Chrome/Edge/Chromium ({last}). Install Google Chrome, or run: python -m playwright install chromium")
        page = await browser.new_page(viewport={"width": 900, "height": 700})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.add_init_script("window.__NO_LOOP = true")
        await page.goto("file:///" + engine.replace("\\", "/").lstrip("/"))
        await page.evaluate("document.fonts.load(\"800 80px Mukta\", \"प्लासी 3,000\")")
        await page.evaluate("Promise.all([document.fonts.load('700 80px Khand', 'प्लासी REC ▶ 1757'), document.fonts.load('800 80px Mukta', 'प्लासी')])")
        info = await page.evaluate("o => studioLoad(o)", {"spec": spec, "timing": timing, "images": images, "narrDur": narr_dur, "sfx": sfx,
                                                         **({"captions": a.captions == "on"} if a.captions else {})})
        if errs:
            sys.exit("ERROR in engine: " + errs[0])
        for w in info["warnings"]:
            print("  check:", w)
        total = info["duration"]
        t0 = max(0.0, a.start or 0.0)
        t1 = min(total, a.end if a.end is not None else total)
        frames = int((t1 - t0) * a.fps)
        W, H = info["W"], info["H"]
        print(f"{vid}: {W}x{H} · {t1 - t0:.1f}s · {frames} frames @ {a.fps}fps · timing from {'timing.json' if timing else 'estimates'}")

        tmp = out[:-4] + ".video_only.mp4"
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-c:v", "mjpeg", "-i", "-",
                                "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-r", str(a.fps), tmp], stdin=subprocess.PIPE)
        start = time.time()
        for i in range(frames):
            t = t0 + i / a.fps
            data = await page.evaluate(f"studioFrame({t:.5f}, {a.quality / 100:.2f})")
            enc.stdin.write(base64.b64decode(data.split(",", 1)[1]))
            if i % (a.fps * 2) == 0 or i == frames - 1:
                el = time.time() - start
                eta = el / (i + 1) * (frames - i - 1)
                print(f"\r  frame {i + 1}/{frames}  ({(i + 1) / frames * 100:4.1f}%)  ETA {int(eta // 60)}m{int(eta % 60):02d}s   ", end="", flush=True)
        enc.stdin.close()
        if enc.wait() != 0:
            sys.exit("\nERROR: ffmpeg failed while encoding video.")
        print()
        sfx_path = None
        if not a.no_sfx:
            wav = await page.evaluate("studioSfxWav()")
            sfx_path = out[:-4] + ".sfx.wav"
            open(sfx_path, "wb").write(base64.b64decode(wav))
        if a.start is None and a.end is None and not a.no_thumb:
            png = await page.evaluate("studioThumb()")
            tp = os.path.join(folder, vid + "_thumbnail.png")
            open(tp, "wb").write(base64.b64decode(png.split(",", 1)[1]))
            if W > H:
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tp, "-vf", "scale=1280:720", tp[:-4] + "_1280.png"], check=False)
                if os.path.exists(tp[:-4] + "_1280.png"):
                    os.replace(tp[:-4] + "_1280.png", tp)
            print("  thumbnail:", tp)
        await browser.close()

    # ---- audio: narration + music + sound effects
    cmd, labels, k = ["ffmpeg", "-y", "-loglevel", "error", "-i", tmp], [], 1
    filt = []
    if narr:
        cmd += ["-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", os.path.join(folder, narr)]
        filt.append(f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo[n]"); labels.append("[n]"); k += 1
    if music:
        cmd += ["-stream_loop", "-1", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", os.path.join(folder, music)]
        filt.append(f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={a.music_volume}[m]"); labels.append("[m]"); k += 1
    if sfx_path:
        cmd += ["-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", sfx_path]
        filt.append(f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={a.sfx_volume}[s]"); labels.append("[s]"); k += 1
    if labels:
        mix = "".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.95[a]" if len(labels) > 1 else labels[0].replace("]", "") + "]"
        if len(labels) > 1:
            filt.append(mix); amap = "[a]"
        else:
            amap = labels[0]
        cmd += ["-filter_complex", ";".join(filt), "-map", "0:v", "-map", amap, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{t1 - t0:.3f}", out]
        subprocess.run(cmd, check=True)
        os.remove(tmp)
        if sfx_path and os.path.exists(sfx_path): os.remove(sfx_path)
    else:
        os.replace(tmp, out)
        print("  (no audio found — video is silent)")
    print(f"Done: {out}")


def main():
    ap = argparse.ArgumentParser(description="Frame-perfect render for History Video Studio")
    ap.add_argument("folder")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--from", dest="start", type=float, help="start second (preview a section)")
    ap.add_argument("--to", dest="end", type=float, help="end second")
    ap.add_argument("--out", help="output file (default: VIDEO_FOLDER/<id>.mp4)")
    ap.add_argument("--engine", help="path to studio_engine.html")
    ap.add_argument("--quality", type=int, default=92, help="frame JPEG quality 70–98")
    ap.add_argument("--crf", type=int, default=18, help="x264 quality (lower = better, 18 is visually lossless)")
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--music-volume", type=float, default=0.12)
    ap.add_argument("--sfx-volume", type=float, default=1.0, help="sound effects & ambience volume (0 = off)")
    ap.add_argument("--no-sfx", action="store_true", help="leave out sound effects & ambience")
    ap.add_argument("--captions", choices=["on", "off"], help="override the scene file's captions setting")
    ap.add_argument("--headed", action="store_true", help="show the browser window (uses the real GPU, often faster)")
    ap.add_argument("--no-thumb", action="store_true")
    ap.add_argument("--browser", default="auto", choices=["auto", "chrome", "msedge", "chromium"], help="which installed browser to use")
    ap.add_argument("--gl", default="default", choices=["default", "swiftshader"], help="swiftshader = software 3D (slow, for machines without a GPU)")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
