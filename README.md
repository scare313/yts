# History Video Studio — engine v1.1 (Time Taped)

New in v1.1: cuts inside scenes, sound effects & ambience, sentence-synced captions with red keywords,
Time Taped tape titles / REC year counter / name cards, VS cards, freeze-frames, battlefield arrows,
evidence-board maps, loop endings, a 12 s end screen for long videos, and pacing checks. See the guide.

Full guide: https://claude.ai/artifact/4you5yLs39hNaX8VEk5q5M

Quick start
1. Open `studio_engine.html` in Chrome/Edge → **Open video folder** → pick `videos/L01-S01` → Space to play.
2. Mine a lecture: `prompts/PROMPT_1_LECTURE_MINER.md` → paste the CSV into `History_Studio_Tracker.xlsx` (Content sheet).
3. Make a video: `prompts/PROMPT_2_PRODUCTION_PACK.md` (new chat per video) → save the JSON files into `videos/<Topic_ID>/`.
4. Voice (Sarvam): `python tools/tts.py videos/<Topic_ID> --provider sarvam --speaker <voice>`   (needs env var SARVAM_API_KEY)
   Pick a voice first: `python tools/tts.py videos/L01-S01 --provider sarvam --audition male`
   ElevenLabs instead: `python tools/tts.py videos/<Topic_ID> --voice YOUR_VOICE_ID` (env var ELEVENLABS_API_KEY)
5. Preview in the engine, fix anything under **Checks**. Warnings, or a scene that feels flat or cluttered? Paste the spec + the Checks text into `prompts/PROMPT_4_SCENE_DOCTOR.md` (new chat) and it returns a repaired file with a changelog.
6. Render: `python tools/render.py videos/<Topic_ID>`  → `<Topic_ID>.mp4` + thumbnail.

Shorts-first: scripts default to 35–45 s with a seamless loop (last line flows into the first). The vocabulary reference lives in `prompts/SCENE_FILE_REFERENCE.md` — the master copy; Prompt 2 and Prompt 4 embed an identical copy, so after editing the master, paste the same change into both.

Setup once: Chrome or Edge · Python 3.10+ · ffmpeg (`winget install Gyan.FFmpeg`) · `pip install playwright`.

Examples: `L01-S01` Plassey Short · `L02-S04` Panipat Short · `DEMO-LONG` every scene type in 16:9 · `DEMO-ASSETS` the newest assets (snow ridge, trench, airfield, PLA, frozen soldiers).
What the engine can draw today is listed in the ASSET LIBRARY section of `prompts/SCENE_FILE_REFERENCE.md` (and the copies inside Prompts 2 and 4). When you add a new asset to the engine, add it to that list too, so the AI uses it instead of reporting it as missing.
Try the voice pipeline for free: `python tools/tts.py videos/L01-S01 --provider sarvam --mock` (silent placeholder audio at speaking pace).
The full guide is also in this folder: History_Video_Studio_Guide.pdf
