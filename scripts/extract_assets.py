#!/usr/bin/env python3
"""Extract posters and teaser figures for the project page.

Usage (from the repo root):
    python3 scripts/extract_assets.py --src ..

where --src is the folder holding Belt_Finger_V1.pdf, Belt_Finger_V2.pdf,
belt_finger_videos/ and belt_finger_touch_videos/.

- Belt-Finger-Touch posters: the author-chosen frames embedded (base64) in
  belt_finger_touch_videos/videos/video_supplement.html.
- Belt-Finger posters: single frames grabbed with ffmpeg at fixed timestamps.
- Teasers: Fig. 1 of each paper, rendered with pdftoppm and trimmed.
Requires: pdftoppm (poppler), Pillow, ffmpeg (or `uv` to fetch one).
"""
import argparse
import base64
import io
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "static" / "images"
POSTERS = IMG / "posters"
POSTER_WIDTH = 1280

# supplement id -> poster name (matches static/videos/touch/<name>.mp4)
TOUCH_POSTERS = {
    "assembly": "assembly",
    "field": "field",
    "reorient": "reorient",
    "pickplace": "pick_place",
    "guidance": "guidance",
    "circular": "circular",
}

# source video -> (poster name, timestamp in s)
V1_POSTERS = {
    "Belt-Finger-Paper-introduction.mp4": ("intro", 1.0),
    "belt_gripper.mp4": ("hardware_teleop", 81.7),
    "gripper_compare_with_teleop.mp4": ("vs_parallel", 1.0),
    "vla-benchmarking.mp4": ("vla", 4.5),
}

# pdf, page, crop box in 400-dpi pixels (left, top, right, bottom), output name
TEASERS = [
    ("Belt_Finger_V1.pdf", 1, (780, 2250, 2640, 2900), "v1_teaser.jpg"),
    ("Belt_Finger_V2.pdf", 2, (240, 230, 1700, 935), "touch_teaser.jpg"),
]


def find_ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    return subprocess.check_output(
        ["uv", "run", "--quiet", "--with", "imageio-ffmpeg", "python", "-c",
         "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())"], text=True).strip()


def save_jpeg(im, path, width=None, quality=85):
    im = im.convert("RGB")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    print(f"  {path.relative_to(ROOT)}  {im.width}x{im.height}  {path.stat().st_size // 1000} kB")


def trim_white(im, pad=30, thresh=12):
    gray = im.convert("L")
    diff = ImageChops.difference(gray, Image.new("L", gray.size, 255))
    x0, y0, x1, y1 = diff.point(lambda p: 255 if p > thresh else 0).getbbox()
    return im.crop((max(0, x0 - pad), max(0, y0 - pad),
                    min(im.width, x1 + pad), min(im.height, y1 + pad)))


def touch_posters(src):
    html = (src / "belt_finger_touch_videos/videos/video_supplement.html").read_text(encoding="utf-8")
    videos = json.loads(re.search(r"const VIDEOS = (\[.*?\]);\n", html, re.S).group(1))
    for v in videos:
        b64 = v["posterData"].split(",", 1)[1]
        im = Image.open(io.BytesIO(base64.b64decode(b64)))
        save_jpeg(im, POSTERS / f"{TOUCH_POSTERS[v['id']]}.jpg", POSTER_WIDTH)


def v1_posters(src, ffmpeg):
    with tempfile.TemporaryDirectory() as tmp:
        for video, (name, t) in V1_POSTERS.items():
            frame = Path(tmp) / f"{name}.png"
            subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t),
                            "-i", str(src / "belt_finger_videos" / video),
                            "-frames:v", "1", str(frame)], check=True)
            save_jpeg(Image.open(frame), POSTERS / f"{name}.jpg", POSTER_WIDTH)


def teasers(src):
    with tempfile.TemporaryDirectory() as tmp:
        for pdf, page, box, out in TEASERS:
            prefix = Path(tmp) / Path(pdf).stem
            subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "400",
                            "-png", "-singlefile", str(src / pdf), str(prefix)], check=True)
            im = Image.open(f"{prefix}.png").convert("RGB")
            save_jpeg(trim_white(im.crop(box)), IMG / out, 1600, quality=88)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=ROOT.parent,
                    help="folder with the paper PDFs and the original video folders")
    src = ap.parse_args().src.resolve()
    POSTERS.mkdir(parents=True, exist_ok=True)
    print("Belt-Finger-Touch posters:")
    touch_posters(src)
    print("Belt-Finger posters:")
    v1_posters(src, find_ffmpeg())
    print("Teasers:")
    teasers(src)


if __name__ == "__main__":
    main()
