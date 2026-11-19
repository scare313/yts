SCENE FILE REFERENCE — History Video Studio engine v1.1 (Time Taped brand)
(Prompt 2 includes this whole block. Only words listed here are understood; anything else is replaced with a safe default and shown under "Checks" in the engine.)

FILE SHAPE (JSON)
{
  "meta": {"id": "L01-V02", "title": "...", "format": "short" | "long", "lang": "hi", "captions": true | false,
           "loop": true (Shorts: last frame blends into the first, default true), "end_card": "अगली कहानी: …" (Shorts: tape note in the last 2 s),
           "end_screen": true (long: 12 s branded end screen for YouTube end-screen links, default true), "look": "diorama" | "flat", "brand": false (turns the Time Taped style off)},
  "characters": {"<key>": {"type": "<character type>", "label": "on-screen name", ...optional overrides}},
  "thumbnail": {"scene": <scene number>, "text": "≤4 words (long: use \n for 2 lines)", "sub": "≤5 words", "year": 1757, "at": 0.7},
  "missing_assets": ["things the engine could not show and what was used instead — check the ASSET LIBRARY first; never list something that is in it"],
  "scenes": [ <scene>, <scene>, ... ]
}
Long videos may be split: spec.json (meta, characters, thumbnail, first scenes) + scenes_02.json, scenes_03.json … each {"scenes": [...]}. The engine joins them in name order.

SCENE
{
  "id": 1,
  "chapter": "अध्याय 2 • ...",       long videos: same value on every scene of a chapter; a banner shows when it changes
  "narration": "words the voice speaks — numbers written as words",
  "caption": "on-screen version — numbers as digits (optional; defaults to narration)",
  "title": "≤5 words, printed on a strip of tape (optional)", "title_style": "red" (red tape, for the hook/twist/final question),
  "keyword": "50,000" or ["गुप्त सौदा", "गद्दी"] — words in the caption to highlight in red (and punch-zoom when they appear),
  "year": 1757 — shows the "● REC ▶ 1757" tape counter (use when a date matters),
  "name_card": {"name": "मीर जाफ़र", "role": "नवाब का सेनापति", "years": "1691–1765"} — lower-third tape label, first time a person appears,
  "shots": [{"at": 0, "camera": "low_angle", "focus": "mj"}, {"at": 0.4, "camera": "close_up", "focus": "mj"}, {"at": 0.75, "camera": "aerial"}]
           — cuts inside the scene ("at" = fraction of the scene). Omit to let the engine cut automatically (~every 2.7 s in Shorts, 4.5 s in long videos). "none" = one shot.
  "freeze": {"at": 0.5, "for": 1.0, "label": "मीर जाफ़र: बस देखते रहे", "target": "mj"} — picture stops, red circle + label on the target, narration continues,
  "sfx": ["impact", {"name": "tape", "at": 0.5, "gain": 0.5}] — extra sounds; "ambience": "rain" | "wind" | "battle" | "night" | "fire" | "sea" | "room" | "crowd" | "none" (default: automatic),
  "setting": "...", "time": "...", "camera": "...", "focus": "<element id | character key | position>",
  "view": "side" | "front" (optional), "zoom": 0.6–1.5 (optional; <1 = closer),
  "elements": [ ... ], "fx": [ ... ], "transition": "cut" (Shorts default) | "fade" (long default) | "flash" | "rewind", "labels": true (tape name labels above characters),
  "map": {...} | "timeline": {...} | "card": {...} | "image": {...}   (only with those settings),
  "color": "#hex"  (background for studio / tent cloth)
}

SETTINGS
  outdoor: battlefield, field, village, river, coast (sea at back), desert, hills, forest, city, fort (fort wall + gate at back), palace (palace at back), temple (temple at back),
           mountain (snow ridge: white ground, snow-capped peaks, snow-dusted boulders), airfield (gravel field with runway, hangar, control tower, tricolour pole and windsock behind the action)
  indoor:  court (durbar hall: pillars, carpet — add a throne prop at "back"), room (default candle), tent (default oil lamp), studio (plain coloured stage)
  special: map, timeline, card, image
TIME: day, golden, dusk, night, dawn, storm, overcast (soft grey light — the look for snow and cold)   (indoor: night = dark + candle/torch light)
CAMERA: wide, aerial, swoop_down, push_in, pull_out, orbit, pan_left, pan_right, low_angle, top_down, crane_up, static,
        close_up*, over_shoulder*, track*     (* focus must be a character)
POSITIONS ("pos"): center, left, right, far_left, far_right, front, front_left, front_right, back, back_left, back_right, far_back
        or [x, z]: x = −30 (left) … 30 (right); z = −30 (far from camera) … 10 (near camera). Indoor scenes use the same numbers (scaled down automatically) — keep them within −8…8.

ELEMENTS
  {"type":"character", "character":"<key>", "id":"<optional id>", "pos":..., "action":"<action>", "face":"left|right|camera|back|<id of an element listed earlier>", "mounted":true, "scale":1, "frost":true}
       ("frost":true = covered in frost and snow, perfectly still: no breathing, no sway. Use with action "stand" or "kneel" for soldiers frozen in the snow. No injury, no bodies.)
  {"type":"army", "id":"...", "faction":"<faction>", "size":"tiny|small|medium|large|huge", "pos":..., "motion":"still|advance|retreat|charge|march",
       "face":"left|right|camera|back", "elephants":true, "cavalry":true, "cannons":3, "banners":true, "flag":"<flag style>", "coat":"#hex", "turban":"#hex"}
  {"type":"cavalry", "faction":"...", "size":"...", "pos":..., "motion":"...", "face":"..."}
  {"type":"crowd", "size":"tiny|small|medium|large", "pos":..., "colors":["#hex", ...]}
  {"type":"prop", "name":"<prop>", "pos":..., "count":1, "spread":4, "on":"table|floor", "scale":1, "face":"..."}
  {"type":"building", "name":"<building>", "pos":..., "rotate":0, "flag":"<flag style>", "color":"#hex", "scale":1}
  {"type":"flag", "style":"<flag style>", "pos":...}
  {"type":"trees", "kind":"mango|palm|pine|banyan", "pos":..., "count":10, "spread":8}
  {"type":"arrow", "from": <position or element id>, "to": <position or element id>, "label":"…", "color":"red", "at":0.1, "curve":0.18, "width":0.5} — a red arrow that grows across the battlefield

CHARACTER TYPES: emperor, king, queen, nawab, noble, minister, general, british_officer, british_soldier, british_official, sepoy, french_officer,
  european_merchant, portuguese, mughal_soldier, maratha_warrior, rajput_warrior, sikh_warrior, afghan_warrior, ancient_warrior, greek_soldier,
  sage, monk, priest, scholar, merchant, farmer, villager, woman, freedom_fighter, leader, modern_soldier (olive uniform, steel helmet, rifle), pla_soldier (Chinese infantry: quilted khaki coat, fur cap with red badge, rifle),
  pla_officer (same, red sash), officer_suit, scientist, child
  overrides: coat, turban, sash, beard, hair, legs, scarf, helmet, vest (colours), hat (turban|tricorne|tophat|crown|helmet|cap|fur_cap|headscarf|bun|none), capColor (cap / fur_cap colour),
  plume (true or colour), sword (true), musket (true), rifle (true = a bolt-action rifle), quilted (true = padded winter coat), spear (true), robe (true = long robe),
  skin (indian|european|afghan|east_asian|african), s (size, 0.7 = child)
  All figures are faceless low-poly; identity comes from clothing colours, hat, beard and the on-screen label.
FACTIONS (armies): british, sepoy, french, portuguese, dutch, mughal, nawab, maratha, rajput, sikh, afghan, mysore, ancient, greek, modern_indian, pla (alias: chinese), rebels, civilians, generic
ACTIONS: stand, point, raise_sword, fight, salute, bow, kneel, walk, talk, wave, hold_letter, hold_scroll, read, celebrate, sit, defeated, turn_to_camera, look_down, think,
  shock, slump, nod, gesture, pray (namaste), beckon
PROPS: cannon, barrel, crate, table, throne, letter, coins, chest, scroll, book, sword, shield, rock, cart, horse, elephant, flag, banner, candle, lamp, torch, campfire, pillar, crown, tree,
  rifle (lying on the ground), rifle_helmet (the soldier's memorial: rifle planted muzzle-down, helmet on the butt), helmet (steel helmet), sandbags (a small stack), ammo_crate (olive-green box), windsock
  (letter, coins, book, scroll, sword, crown, candle sit on the table automatically when the scene has a table; props placed ON a trench rest on its floor)
BUILDINGS: house, hut, temple, dome (mosque/tomb), palace, fort, wall, tower, gate, stupa, tent, ship, boat, well, bridge,
  trench (dark channel between two sandbagged banks — soldiers placed on it stand waist-deep in it), sangar (crescent of dry-stone wall), hangar, airstrip (runway), aircraft (twin-engine transport plane, propellers spin)
FLAG STYLES: eic (East India Company), union (British), tricolour (India), french, china (PRC), saffron (bhagwa), mughal (green), or any colour name / "#hex"
FX: rain, lightning, smoke, fire, fog, dust, embers, snow, desaturate (colour drains in the 2nd half), sepia, shake, flash
COLOUR NAMES: red, maroon, crimson, saffron, orange, yellow, gold, green, darkgreen, blue, navy, purple, white, black, grey, brown, pink, teal, cream, olive — or "#rrggbb"

ASSET LIBRARY — everything the engine can draw today. Look HERE before you write "missing_assets": if it is listed, USE it and do not report it as missing.
  HOW THE NEWER ASSETS BEHAVE
  • mountain: snow ridge. Pair it with time "overcast" (flat grey cold light) or "dawn"; add fx "snow" for falling snow and "fog" for a whiteout yourself. For a blizzard use time "storm".
  • airfield: the runway, hangar, control tower, tricolour pole and windsock are already there behind the action. Add "aircraft", tents and people in front of them.
  • trench: film it from ABOVE (top_down, aerial, crane_up) to see inside it; from low_angle the near sandbag bank hides what is inside. For a "lone rifle in an empty trench" put a "rifle" prop and no characters on it.
  • rifle_helmet: the memorial image (rifle planted muzzle-down, helmet on the butt) — a strong closing frame for a sacrifice story. "helmet" and "rifle" lying on the ground tell "someone was here and is gone" without showing anyone.
  • pla / pla_soldier / pla_officer + flag "china": the Chinese army of 1962 (quilted khaki coat, fur cap with red badge, rifles). modern_soldier / modern_indian: Indian soldiers with steel helmets and rifles (not muskets).
  • "frost":true on a character: the figure is frosted white and stands completely still. Three or four of them kneeling and standing in snow + fog is how to show "found frozen at their posts". Never show injury or bodies.
  STORY KITS — which assets to reach for
  • Mughal / Maratha / Rajput / Sikh / Afghan courts and battles: court (throne at "back"), fort, palace, tent; armies with elephants, cavalry, cannons, banners; the matching faction and character types.
  • East India Company, 1757 and 1857: british, sepoy, french, dutch, portuguese factions; british_officer, british_official; ship, fort, tent; flags eic / union; room or tent for secret meetings.
  • Freedom struggle: freedom_fighter, leader, crowd (with "colors"), village, city, temple; flag tricolour; a room for secret meetings.
  • Wars of independent India (1947–1999): modern_soldier / modern_indian; mountain, hills, desert, airfield; trench, sangar, sandbags, ammo_crate, rifle, helmet, rifle_helmet, aircraft; flag tricolour; for the 1962 opponent use pla. For any other opponent use the closest faction with a coat/turban colour override.
  • Ancient and classical: ancient and greek factions; stupa, temple, wall, gate; ancient_warrior, greek_soldier, sage, monk.
  NOT AVAILABLE YET — use the substitute and list it in missing_assets
  • tanks, jeeps, trucks, helicopters, jet fighters, trains, submarines, modern warships → closest: cart, aircraft (a transport plane), ship (a sailing ship), or say it in the narration and show soldiers.
  • machine guns, mortars, radios, binoculars, medals, rank insignia → show soldiers with crate / rifle / sandbags and name the weapon in the narration and caption.
  • specific monuments (Taj Mahal, Red Fort, Gateway of India, Qutub Minar, Jallianwala Bagh) → dome / fort / gate / tower with a "color" override, and name it with a title tape.
  • real faces, portraits, readable writing on documents or signs, maps outside South Asia with real borders → characters with name_card; a "letter" prop; map with base "none" and places.
  • animals other than horse and elephant (camels, mules, yaks) → horse, or leave them out.

SPECIAL SETTINGS
  map:      {"base":"india" | "none",
             "places":[{"id":"plassey","name":"प्लासी","lat":23.80,"lon":88.25,"highlight":true}],
             "rivers":[{"name":"गंगा","points":[[lat,lon],[lat,lon],...]}],
             "routes":[{"from":"<place id>","to":"<place id>","color":"red","label":"..."} or {"points":[[lat,lon],...],...}],
             "areas":[{"label":"मराठा क्षेत्र","lat":18.5,"lon":74.5,"radius_km":220,"color":"saffron"}],
             "tokens":[{"at":"<place id>","faction":"maratha"}],
             "focus":"<place id>" (zooms to it; omit to show everything), "zoom":{"lat":..,"lon":..,"span_km":..} (manual)}
            Use real coordinates (2 decimals). "india" draws a simplified subcontinent; use "none" for regions outside South Asia.
  timeline: {"events":[{"year":"1757","label":"प्लासी"}, ...], "focus": <index of the highlighted event, 0-based>}
  card:     {"text":"50,000", "sub":"one short line", "color":"#hex", "count": true}  — one big number (counts up automatically), date or very short quote
            {"vs":["3,000","50,000"], "vs_labels":["अंग्रेज़","नवाब"]} — split-screen comparison, both numbers count up
  image:    {"file":"L01-V02_s14.png", "motion":"zoom_in|zoom_out|pan_left|pan_right|pan_up"} — an image you put in the video folder

SOUND (automatic): dhol + impact on the hook, whoosh on every cut, tape slap on titles/labels, ticks on counters, rewind on chapter changes,
  thunder with lightning, background ambience chosen from setting/time/fx. Override with "sfx" / "ambience".

COMPOSITION RULES (what looks good)
  1. One visual idea per scene, 4–8 seconds (Hindi narration ≈ 2.6 words/second → 10–20 words per scene). Shorts: the picture must change at least every 3 s — use shots.
  2. Vertical Shorts: two armies at "left" and "right" are filmed from the side automatically — the "left" army is in the foreground. Put the side you want close at "left".
  3. Keep everything in one scene within ~10 units of each other unless it is a big battle. Don't put crowds at "front" in front of the main character.
  4. close_up / over_shoulder / track need "focus": a character key. Use them for emotional beats (decision, betrayal, reaction).
  5. Change setting at least every 2–3 scenes; never the same setting + camera twice in a row.
  6. Use map when places/routes matter, timeline when dates matter, card for one big number — together ≤ 20% of scenes.
  7. Max 4 light sources per scene (candle, lamp, torch, campfire, fire).
  8. No gore: fight, charge and defeated are fine; no blood or bodies.
  9. If something cannot be shown (e.g. a specific monument), use the closest building/prop and add a line to missing_assets — but look in the ASSET LIBRARY first and only list what is truly missing and matters to the story, with the substitute you used.
  10. Scene 1 (hook): motion from frame one (swoop_down / low_angle / fx flash), a red title, the key number as keyword.
  11. Every scene gets a keyword; a person's first appearance gets a name_card; a date that matters gets year.
  12. Use a "vs" card when the story is a contrast, a freeze when one person's choice is the turning point, arrows for movement on battlefields.
  13. Court, room and tent come pre-dressed (dais, braziers, shelf, poles, chest…). Don't spend elements on basic furniture — spend them on the story objects (letter, coins, throne, the people).
  14. pan_left / pan_right glide along the content, so spread the scene's elements along the left–right axis with something at both ends. Two clusters more than ~25 units apart leave dead frames in between.

SHORTS-FIRST RULES (this channel makes vertical Shorts; long videos are the exception)
  S1. Frame one: the hook scene must show its contrast with the sound off — two visibly unequal armies, one huge number card, a lone figure facing a crowd. The caption is on screen from 0.0 s.
  S2. Spoken hook ≤ 8 words, no greeting. The open question appears by second 3.
  S3. Mute-first: captions + red keywords alone must carry the story. The picture adds something; it never just repeats the words.
  S4. Phone screen: one person, one object, one idea per scene. Use close_up / low_angle / push_in on the main figure for emotional beats; huge armies only as backdrop behind one clear subject. At most ONE map scene per Short; no timeline unless the dates ARE the story.
  S5. Safe zones (9:16): keep key action in the middle 60% of the frame height. YouTube's own title, buttons and subscribe bar cover the bottom ~20% and right ~15%.
  S6. Re-hook at ~12–15 s (a new question, a number, a "लेकिन…") and the twist at ~60%. Pace: a new picture at least every 3 s.
  S7. Loop: the last narration line must flow into the first one — end on a clause or question that the opening line completes ("…तो प्लासी में असली जीत किसकी थी? जवाब है —" → "सिर्फ़ तीन हज़ार सैनिक…"). meta.end_card is OPTIONAL: it appears in the last 2 s and can break the loop, so use it only when you want to push to the next story.

SOUND DIRECTION (valid sfx names: drum, impact, rewind, tape, thunder, tick, whoosh)
  Already automatic: drum+impact on the hook, whoosh on every cut, tape on titles and name cards, impact+ticks on number cards, impact+tape on freeze, thunder with lightning, rewind on chapter changes.
  So spend "sfx" only where nothing fires automatically: one deliberate hit every 2–3 scenes on a reveal — {"name":"impact","at":0.6,"gain":0.5} on the number or the betrayal line, "tape" on a document or label moment, "drum" before the twist.
  Silence is a tool: "ambience":"none" for the first beat of the twist scene makes the next impact land harder. Set ambience explicitly when the automatic one is wrong (tense indoor day scene → "night"; calm hilltop → "wind"). At most 2 sfx entries per scene.

GOLDEN SCENES (copy the blocking, not the story)
  A. HOOK — the contrast is visible with the sound off. Small army at "left" is the near, foreground side; the huge one at "far_right" is the threat.
  {"id":1,"narration":"सिर्फ़ तीन हज़ार सैनिक…","caption":"सिर्फ़ 3,000 सैनिक…","keyword":"3,000","title":"प्लासी 1757","title_style":"red","setting":"battlefield","time":"storm","camera":"swoop_down","focus":"brit",
   "elements":[{"type":"army","id":"brit","faction":"british","size":"small","pos":"left","cannons":3},{"type":"army","faction":"nawab","size":"huge","pos":"far_right","elephants":true,"cavalry":true,"banners":true}],"fx":["lightning"]}
  B. CONSPIRACY — three people and the objects that matter, all within ±7 units; a light source at night; one slow push_in.
  {"id":4,"narration":"असली लड़ाई मैदान में नहीं… बंद कमरों में लड़ी जा चुकी थी।","caption":"असली लड़ाई मैदान में नहीं… बंद कमरों में लड़ी जा चुकी थी।","keyword":"बंद कमरों","title":"असली लड़ाई?","setting":"room","time":"night","camera":"push_in","focus":"center",
   "elements":[{"type":"prop","name":"table","pos":"center"},{"type":"prop","name":"letter","pos":"center"},{"type":"prop","name":"coins","pos":[-3.5,0.5]},{"type":"character","character":"seth","pos":[0,-6.5],"action":"gesture"},{"type":"character","character":"agent","pos":[7,2.8],"action":"point"},{"type":"character","character":"mirjafar","pos":[-7,2.5],"action":"nod"}]}
  C. PERSON ON SCREEN — first appearance gets a name_card; one character, face to camera, three shots (close → orbit → close) so the picture changes every ~2.5 s.
  {"id":5,"narration":"नवाब के सेनापति मीर जाफ़र ने अंग्रेज़ों से गुप्त सौदा कर लिया था।","caption":"नवाब के सेनापति मीर जाफ़र ने अंग्रेज़ों से गुप्त सौदा कर लिया था।","keyword":["गुप्त सौदा"],"name_card":{"name":"मीर जाफ़र","role":"नवाब का सेनापति","years":"1691–1765"},
   "setting":"tent","time":"night","camera":"close_up","focus":"mirjafar","shots":[{"at":0,"camera":"close_up","focus":"mirjafar"},{"at":0.45,"camera":"orbit","zoom":0.8},{"at":0.75,"camera":"close_up","focus":"mirjafar"}],
   "elements":[{"type":"character","character":"mirjafar","pos":"center","face":"camera","action":"hold_letter"}]}
  D. TURNING POINT — one freeze on the person whose choice mattered, an arrow for the movement, a deliberate silence before it.
  {"id":7,"narration":"मीर जाफ़र की टुकड़ियाँ बस खड़ी देखती रहीं।","caption":"मीर जाफ़र की टुकड़ियाँ बस खड़ी देखती रहीं।","keyword":["खड़ी देखती रहीं"],"title":"धोखा","title_style":"red","setting":"hills","time":"storm","camera":"wide","focus":"mj","ambience":"none",
   "sfx":[{"name":"drum","at":0.3,"gain":0.5}],"shots":[{"at":0,"camera":"low_angle","focus":"mj"},{"at":0.4,"camera":"close_up","focus":"mj"},{"at":0.75,"camera":"aerial"}],
   "freeze":{"at":0.45,"for":1.0,"label":"मीर जाफ़र: बस देखते रहे","target":"mj"},
   "elements":[{"type":"character","id":"mj","character":"mirjafar","pos":[-6,3],"mounted":true,"face":"right"},{"type":"army","id":"fleeing","faction":"nawab","size":"medium","pos":"far_right","motion":"retreat","face":"left"},{"type":"army","faction":"british","size":"small","pos":"right","motion":"advance","face":"right"},{"type":"arrow","from":[12,2],"to":[28,-6],"label":"बिखरती सेना","at":0.2}],"fx":["smoke","desaturate"]}
  BAD → FIX (pan with a gap):
  BAD:  pan_right, barrels at [-14,1], one lone cannon at [26,-8] → 40 units of empty grass between them, dead frames mid-pan.
  FIX:  pan_right, barrels at [-9,1] and a soldier at [-7,3] (story object), cannons at [-3,4], nawab's wet cannons at [7,1.8], an army at [10,-2] → the pan travels through things the narration is talking about.

PRE-FLIGHT CHECKLIST (run silently on the finished scene list BEFORE printing the JSON; fix every violation)
  [ ] Every scene's narration ≤ 22 words (Shorts) and its caption/keyword match the approved table character for character.
  [ ] Scene 1: camera is moving, title_style "red", contrast visible with sound off, key number is the keyword.
  [ ] Last narration line flows into the first line (loop). end_card only if wanted.
  [ ] No setting + camera repeated in consecutive scenes; settings change at least every 2–3 scenes.
  [ ] close_up / over_shoulder / track always have a character as focus.
  [ ] Every scene longer than ~5 s has "shots"; no single shot > 3.5 s.
  [ ] All elements in a scene within ~10 units (battles ≤ 25; pan scenes spread along x with content at both ends).
  [ ] At most one map scene, and map + timeline + card ≤ 20% of scenes.
  [ ] Every scene has a keyword; first appearance of a person has a name_card; every date that matters has a year.
  [ ] Troop movement has an arrow; numeric contrast has a "vs" card; the decision scene has ONE freeze.
  [ ] 2–4 deliberate sfx moments; ambience set where the automatic one would be wrong.
  [ ] missing_assets lists ONLY things that are absent from the ASSET LIBRARY (and matter to the story), each with the substitute used. Nothing in the library is reported as missing.
  [ ] Valid JSON: double quotes, no comments, no trailing commas.
