#!/usr/bin/env bash
# Re-encode the original paper videos into web-friendly H.264 for GitHub Pages.
#
# Usage: bash scripts/encode_videos.sh <belt_finger_videos_dir> <belt_finger_touch_videos_dir>
#
# GitHub rejects files > 100 MB and warns above 50 MB, and GitHub Pages does not
# serve Git LFS objects, so every output must stay below MAX_MB. Originals are
# kept outside this repo.
set -euo pipefail

V1_SRC=${1:?"usage: $0 <belt_finger_videos_dir> <belt_finger_touch_videos_dir>"}
TOUCH_SRC=${2:?"usage: $0 <belt_finger_videos_dir> <belt_finger_touch_videos_dir>"}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="$ROOT/static/videos"
MAX_MB=50

# ffmpeg: $FFMPEG, else system ffmpeg, else a static build via uv + imageio-ffmpeg.
if [[ -z "${FFMPEG:-}" ]]; then
  if command -v ffmpeg >/dev/null; then
    FFMPEG=ffmpeg
  else
    FFMPEG=$(uv run --quiet --with imageio-ffmpeg python -c \
      "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())")
  fi
fi
echo "ffmpeg: $FFMPEG"

mkdir -p "$OUT/v1" "$OUT/touch"

# copy <src> <dst>: source is already web-friendly; remux only (adds faststart).
copy() {
  "$FFMPEG" -hide_banner -loglevel error -y -i "$1" -map 0 -c copy -movflags +faststart "$2"
}

# encode <src> <dst> <max_height> <maxrate> [crf]
encode() {
  "$FFMPEG" -hide_banner -loglevel error -stats -y -i "$1" \
    -map 0:v:0 -map '0:a?' \
    -vf "scale=-2:'min($3,ih)'" \
    -c:v libx264 -preset slow -crf "${5:-26}" -maxrate "$4" -bufsize "$4" \
    -pix_fmt yuv420p -profile:v high \
    -c:a aac -b:a 96k \
    -movflags +faststart "$2"
}

# --- Belt-Finger (V1) ---
encode "$V1_SRC/Belt-Finger-Paper-introduction.mp4" "$OUT/v1/intro.mp4"           720  1200k 24
encode "$V1_SRC/belt_gripper.mp4"                   "$OUT/v1/hardware_teleop.mp4" 720  1800k
copy   "$V1_SRC/gripper_compare_with_teleop.mp4"    "$OUT/v1/vs_parallel.mp4"
encode "$V1_SRC/vla-benchmarking.mp4"               "$OUT/v1/vla.mp4"             1080 3000k

# --- Belt-Finger-Touch (V2) ---
copy   "$TOUCH_SRC/tactile_assembly_v4.mp4"                "$OUT/touch/assembly.mp4"
encode "$TOUCH_SRC/test_in_the_field.mp4"                  "$OUT/touch/field.mp4"      1080 3000k
encode "$TOUCH_SRC/fruit_manipulation.mp4"                 "$OUT/touch/reorient.mp4"   1080 3000k
encode "$TOUCH_SRC/pick_fruit.mp4"                         "$OUT/touch/pick_place.mp4" 1080 3000k
encode "$TOUCH_SRC/tactile_guidance.mp4"                   "$OUT/touch/guidance.mp4"   1080 3000k
encode "$TOUCH_SRC/tactile_guidance_circular_movement.mp4" "$OUT/touch/circular.mp4"   1080 3000k

echo
fail=0
for f in "$OUT"/v1/*.mp4 "$OUT"/touch/*.mp4; do
  mb=$(( $(stat -c %s "$f") / 1000000 ))
  printf '%6s MB  %s\n' "$mb" "${f#"$ROOT"/}"
  if (( mb >= MAX_MB )); then
    echo "  ERROR: ${f#"$ROOT"/} is >= $MAX_MB MB" >&2
    fail=1
  fi
done
du -sh "$OUT"
exit "$fail"
