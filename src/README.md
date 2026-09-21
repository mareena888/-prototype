# Band Ladder — IELTS Academic trainer

Two published Artifacts plus the sources that build them.

| Piece | Where |
|---|---|
| Study app | https://claude.ai/artifact/FcKdhU65K2ABNALPd234Py |
| Progress page | https://claude.ai/artifact/75oBvZHSdqWv4q16g7Ax7B |

## Build

```
python3 gen_audio.py     # Piper -> audio/<id>-{w,s}.mp3  (needs piper-tts + ffmpeg)
python3 assemble.py      # content.json + practice.json -> template.html -> app.html
```

- `content.json` — the card corpus, keyed by deck day. 5 words + 3 phrases + 1 grammar per day.
- `practice.json` — the reading passage, writing set and speaking sets. Authored only for a
  practice day; adding a `reading` key to a day is what advances the practice counter.
- `template.html` — the app, with a `/*__DAYS__*/` placeholder.
- `progress.html` — the companion charts, standalone.

## The two counters

`deckDay` is the highest day in `DAYS` carrying a `cards` array; `practiceDay` is the highest
carrying a `reading` object. The daily task only ever appends `cards`, so new vocabulary can
never bury an unfinished passage.

## Audio

External media is blocked by the artifact CSP and browser `speechSynthesis` fails silently on
iOS with the ringer off, so every clip is synthesized with Piper (`en-us-ryan-high`) and
published alongside the page. `speechSynthesis` remains only as a visible-failure fallback.

## Daily task

Trigger `trig_01MJKnaezbHBsmNrdtrtmiiQ`, `0 10 * * *` UTC (18:00 Taipei): appends one
deck-only day at the `DECK APPEND POINT` marker, verifies the JS parses, republishes to the
same URL, then syncs reading results into the progress page.
