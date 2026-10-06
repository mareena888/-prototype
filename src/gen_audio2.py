#!/usr/bin/env python3
"""Synthesize the Recap (second) example sentence for every card -> audio2/<id>-s2.mp3"""
import json, os, subprocess, sys, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(BASE, "piper", "en-us-ryan-high.onnx")
OUT = os.path.join(BASE, "audio2")
os.makedirs(OUT, exist_ok=True)

e2 = json.load(open(os.path.join(BASE, "example2.json"), encoding="utf-8"))

def synth(text, out_mp3):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        wav = tf.name
    try:
        p = subprocess.run(
            [sys.executable, "-m", "piper", "--model", MODEL,
             "--length-scale", "1.05", "--output_file", wav],
            input=text.encode("utf-8"), capture_output=True)
        if p.returncode != 0 or not os.path.getsize(wav):
            raise RuntimeError(f"piper failed: {p.stderr.decode()[:200]}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-ac", "1", "-ar", "22050", "-b:a", "48k", out_mp3], check=True)
    finally:
        os.path.exists(wav) and os.unlink(wav)

items = sorted(e2.items())
for i, (cid, text) in enumerate(items, 1):
    dest = os.path.join(OUT, f"{cid}-s2.mp3")
    if os.path.exists(dest) and os.path.getsize(dest) > 500:
        continue
    synth(text, dest)
    if i % 20 == 0:
        print(f"[{i}/{len(items)}]", flush=True)

sizes = [os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)]
print(f"{len(sizes)} clips, total {sum(sizes)/1024/1024:.2f} MB, mean {sum(sizes)/len(sizes)/1024:.1f} KB")
