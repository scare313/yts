PROMPT 1 — LECTURE MINER  (one long lecture ➜ long-video topics + Shorts topics)
Copy everything below the line into Claude or Gemini (they handle 3–4 hour transcripts in one go). Edit SETTINGS, paste USED TOPICS, attach the transcript.
--------------------------------------------------------------------------------

SETTINGS
- LECTURE_ID: L01
- LECTURE_TITLE: [title of the source video]
- CHANNEL_NAME: [your channel]
- LANGUAGE: Hindi (simple spoken Hindi)
- AUDIENCE: curious viewers 16–35 + UPSC/MPSC aspirants
- LONG_VIDEO_LENGTH: 8–15 minutes
- MAX_LONG_VIDEOS: 10
- SHORTS_PER_LONG: 4–6   (plus up to 10 standalone Shorts)

USED TOPICS (already made or planned — avoid repeating them)
[paste the Working_Title column of the Content sheet here, or write "none"]

YOUR ROLE
You are a history content strategist and story editor. You turn a long coaching lecture into a plan for a YouTube channel that tells history as gripping stories, made with a low-poly 3D animation engine.

STEP 1 — LECTURE MAP
The transcript is auto-generated: no punctuation, misheard names and dates. Read all of it and silently fix obvious errors.
Give a short map of the lecture: one line per section with its location (timestamp if present, otherwise the first 6–8 words of that passage) and what it covers.

STEP 2 — LONG VIDEOS (8–15 min each)
Find up to MAX_LONG_VIDEOS self-contained stories. Each must stand alone for a viewer who never saw the lecture.
- A strong central question or conflict ("How did 3,000 men take Bengal?"), 3–6 acts, a clear payoff.
- Enough material for 1,300–2,300 spoken Hindi words. Don't split one story thin; merge sections if the story needs it.
- Prefer stories with conflict, betrayal, turning points, surprising numbers, journeys across a map, and before/after consequences that still matter today.
- Visual fit: the engine can show battles and armies (British, Mughal, Maratha, Rajput, Sikh, Afghan, Mysore, ancient…), maps with routes and places, durbars, forts, palaces, temples, ships, villages, secret meetings in rooms and tents, timelines and big-number cards. Score down topics that are mostly abstract (economic theory, lists of acts) unless you find a story angle.
- Mark any topic that overlaps USED TOPICS in Duplicate_Of.

STEP 3 — SHORTS (35–45 s each; Shorts are this channel's main product)
- For every long video, SHORTS_PER_LONG Shorts cut from its strongest single moments. Each Short needs its own hook in the first 2 seconds and a payoff; it must work alone AND make people want the long video.
- Then up to 10 standalone Shorts from moments that don't belong to any long video (Parent_ID empty).
- One idea per Short. A twist, a shocking number, a "nobody tells you this", a one-line consequence.
- THE MONEY SHOT: every Short must name the single image a viewer sees in frame one with the sound off (e.g. "3,000 redcoats facing an army of 50,000 under a storm"). If you cannot name one picture the engine can build (armies, a durbar, a secret meeting, a big number, a map route), it is not a Short — drop it or find another angle.
- Prefer ONE person's decision as the spine: a Short about a person choosing something is easier to hold than a Short about a process.
- It should still make sense when its last line loops into its first line, so give it a closing question or an unfinished clause the opening can complete.

STORY SPINE (all topics): before scoring any topic, write one sentence "X wanted Y, but Z" (e.g. "Siraj wanted to crush a trading company, but his own general had already sold him out"). If you cannot fill all three slots, the topic is a list, not a story — score it down or merge it.

RULES
- Originality: the transcript is a research guide only. Topic titles and hooks must be your own words, never the lecturer's lines, jokes or mnemonics, and never mention the lecturer, channel or institute.
- Accuracy: if a claim in the lecture is disputed or likely wrong, say so in Story_Beats ("⚠ verify: …").
- Number IDs: long videos LECTURE_ID-V01, V02…; Shorts LECTURE_ID-S01, S02… (Parent_ID = the V-id they come from).

OUTPUT
1. The lecture map (Step 1) as a short table.
2. A summary table of long videos: ID | Working title | Hook | Est. minutes | Score.
3. ONE CSV code block (```csv) with ALL long videos and ALL Shorts, for the Content sheet. Every field in double quotes, "" for quotes inside a field, no line breaks inside fields, header row exactly:
Topic_ID,Lecture_ID,Type,Parent_ID,Working_Title,Hook_Angle,Story_Beats,Era,Key_People,Places,Transcript_Location,Est_Length,Score,Duplicate_Of
   - Type: Long or Short
   - Working_Title: in LANGUAGE, ≤ 70 characters, curiosity + keyword
   - Hook_Angle: the first line a viewer would hear (LANGUAGE)
   - Story_Beats: start with "SPINE: X wanted Y, but Z" then " | ". Long = acts separated by " | " (Act 1: … | Act 2: …); Short = setup | turn | payoff | MONEY SHOT: the frame-one image
   - Era: e.g. "1757, Bengal" · Key_People: comma-separated · Places: comma-separated
   - Est_Length: Long = minutes (e.g. 12), Short = seconds (e.g. 40)
   - Score: 1–10 (story strength × visual fit × search interest)
   - Duplicate_Of: the USED TOPIC it overlaps, or empty
If the output is too long for one reply, finish whole rows, then say "Type CONTINUE" and continue without repeating the header.

--------------------------------------------------------------------------------
TRANSCRIPT
[attach the .txt file or paste the transcript here]
