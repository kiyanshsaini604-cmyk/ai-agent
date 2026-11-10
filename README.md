# 🐦‍🔥 PHOENIX — Animated Voice Background

An animated background page built from `Blazing Phoenix Ascendant.png`: flapping wings,
ember particle surges, a rotating HUD halo ring, a ticking clock, and a voice-only
command layer — **no typing anywhere**.

## Run

```bash
# from this folder
python -m http.server 8123
# open http://127.0.0.1:8123/index.html
```

A server is required (speech + assets work best over http). Open in **Chrome/Edge** and
allow the microphone when prompted.

## How to talk to Phoenix (voice only)

| Input | Result |
|---|---|
| Say **"Hey Phoenix"** | Wake word — status flips to `LISTENING`, then keep talking |
| Say **"Hey Phoenix, what time is it"** | Command given in one breath |
| Press **[SPACE]** | Push-to-talk (desktop) |
| Tap the **mic button** 🎙 (bottom-left) | Push-to-talk (mobile / touch) |
| Say **"stop / quiet / silence"** | Immediately shuts up and closes the window |

No text ever appears on screen except the original artwork text, the status chip, the
hint line, the clock (time + date, bottom-right) and the command window while open.

## What happens on a command

1. Status → `PROCESSING`: wings flap faster, particles surge from both wings,
   the halo ring spins 80s → 7s with a radar sweep, the mic button glows.
2. A **Phoenix-style command window** opens (`◆ PHOENIX · COMMAND CHANNEL`)
   showing `YOU` — exactly what you asked — then `PHOENIX` — his reply.
   It's draggable (mouse + touch) and has a close ×.
3. He **speaks the reply in a deep monster voice** (`pitch 0.1`, `rate 0.85`,
   deepest male voice available — Microsoft David on Windows).
4. At the very end he **asks you a follow-up question** (also spoken, highlighted
   in the window) and returns to listening for your answer.

Supported intents: time, date, hello, who-are-you, status/diagnostic, flap/dance,
joke, thanks, stop — anything else gets an "logged in working memory" reply.

## Responsive design

Verified with an iframe harness (`debug/responsive_test.html?w=&h=`) on:

- 📱 Phone portrait `390×844` — fit-width stage, edge fade, 92vw window,
  "TAP THE MIC" hint, smaller type
- 📱 Phone landscape `844×390` — short-height compact styles
- 📋 Tablet portrait `768×1024`
- 🖥 Desktop `1280×800` — full-size styles

All checks pass: header/clock/hint/mic inside the viewport, no scrolling, correct
media-query styles, mic button functional. UI layers are `position:fixed` to the
viewport so they never crop, while the image stage keeps its 3:2 cover behavior.

## Files

```
index.html                     ← the deliverable (single file: CSS + JS + voice engine)
assets/phoenix_base.png        ← inpainted base (rings + bird body)
assets/wing_left/right.png     ← feathered wing cutouts (animated)
assets/bird_mask.png           ← masks the rotating ring behind the bird
tools/prep_assets.py           ← regenerates all assets from the source PNG
debug/responsive_test.html     ← sized-iframe test harness (?w=390&h=844)
Blazing Phoenix Ascendant.png  ← original source image
```

Rebuild assets: `python tools/prep_assets.py` (needs OpenCV: `pip install opencv-python numpy`).

## Integration API

```js
// drive the visual state from your own code
PhoenixBackground.setState("processing" | "idle");
window.dispatchEvent(new CustomEvent("phoenix:state", { detail }));

// feed a transcript straight into the voice pipeline (as if spoken)
PhoenixVoice.hear("what time is it");

// helpers
PhoenixVoice.press();            // same as pressing space
PhoenixVoice.wake("hey phoenix turn on the lights");  // { full, tail } or null
PhoenixVoice.mode;               // 'wake' | 'cmd' | 'off'
PhoenixVoice.supported;          // SpeechRecognition available?
```

## Notes

- Uses the Web Speech API: `SpeechRecognition` for listening, `speechSynthesis`
  for the deep voice. Both need Chrome/Edge (or another Chromium browser).
- The OpenCode app's embedded browser hard-denies microphone access, so the status
  shows `MIC NEEDED` there — open the page in a normal browser window instead.
- Audio blips use a small WebAudio synth (created on first interaction).
