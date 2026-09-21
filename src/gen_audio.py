#!/usr/bin/env python3
"""Synthesize word + sentence audio for every card with Piper, encode to mono mp3."""
import json, os, re, subprocess, sys, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
PIPER_DIR = os.path.join(BASE, "piper")
MODEL = os.path.join(PIPER_DIR, "en-us-ryan-high.onnx")
OUT = os.path.join(BASE, "audio")
os.makedirs(OUT, exist_ok=True)

# Grammar cards need a speakable form of their pattern name.
SAY_WORD = {
    "g-not-only-inversion": "Not only, with inversion.",
    "g-the-extent-to-which": "the extent to which",
    "g-were-to-inversion": "Were, plus subject, plus to, plus verb.",
}

def strip_ipa_note(text):
    # "verb /ˌɔfˈsɛt/ · noun /ˈɔfˌsɛt/" never reaches here; items are plain.
    return re.sub(r"\s+", " ", text).strip()

def synth(text, length_scale, out_mp3):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        wav = tf.name
    try:
        p = subprocess.run(
            [sys.executable, "-m", "piper", "--model", MODEL,
             "--length-scale", str(length_scale), "--output_file", wav],
            input=text.encode("utf-8"), capture_output=True)
        if p.returncode != 0 or not os.path.getsize(wav):
            raise RuntimeError(f"piper failed for {text!r}: {p.stderr.decode()[:300]}")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
             "-ac", "1", "-ar", "22050", "-b:a", "48k", out_mp3],
            check=True)
    finally:
        os.path.exists(wav) and os.unlink(wav)

def main():
    days = json.load(open(os.path.join(BASE, "content.json"), encoding="utf-8"))
    jobs = []
    for day, cards in days.items():
        for c in cards:
            cid = c["id"]
            word = SAY_WORD.get(cid, strip_ipa_note(c["item"]))
            jobs.append((f"{cid}-w", word, 1.25))
            jobs.append((f"{cid}-s", strip_ipa_note(c["example"]), 1.05))

    total = len(jobs)
    for i, (name, text, ls) in enumerate(jobs, 1):
        dest = os.path.join(OUT, f"{name}.mp3")
        if os.path.exists(dest) and os.path.getsize(dest) > 500:
            continue
        synth(text, ls, dest)
        print(f"[{i}/{total}] {name}  {os.path.getsize(dest)}B  {text[:60]}")

    sizes = [os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)]
    print(f"\n{len(sizes)} clips, total {sum(sizes)/1024:.0f} KB, "
          f"mean {sum(sizes)/len(sizes)/1024:.1f} KB, max {max(sizes)/1024:.1f} KB")

main()
