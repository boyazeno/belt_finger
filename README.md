# Belt-Finger project page

Project page for the Belt-Finger series, served by GitHub Pages at
**https://boyazeno.github.io/belt_finger/**

- **Belt-Finger**: An Affordable Soft Belt-Driven Gripper for Dexterous In-Hand Manipulation (CoRL 2026, [arXiv:2606.20193](https://arxiv.org/abs/2606.20193))
- **Belt-Finger-Touch**: Integrating Visual-Tactile Sensing for Sensitive In-hand Manipulation (under review)

It is a single static page (`index.html` + `static/`) with no build step.

## Preview locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Open the page through a server rather than as `file://`. Some browsers block local video playback from `file://` URLs.

## Deploy

1. `git push -u origin main`
2. On GitHub, go to **Settings → Pages → Build and deployment**, choose *Deploy from a branch*, then pick `main` and `/ (root)`.
3. The site appears at https://boyazeno.github.io/belt_finger/ after a minute or two.

`.nojekyll` makes Pages serve the files as they are, without running Jekyll.

## Videos

The originals (668 MB, several files over GitHub's 100 MB limit) are **not** in this repo. They were re-encoded to web H.264
with `+faststart` (about 75 MB in total, every file under 50 MB):

```bash
bash scripts/encode_videos.sh ../belt_finger_videos ../belt_finger_touch_videos/videos
```

The script fetches a static ffmpeg through `uv` if none is installed, and fails if any output reaches 50 MB.
Git LFS cannot be used, because GitHub Pages does not serve LFS files.

Re-encoding a video that is already committed adds a new copy to the git history permanently. Settle on the final videos
before committing them.

Posters and the two teaser figures (Fig. 1 of each paper) are regenerated with:

```bash
python3 scripts/extract_assets.py --src ..
```

## Filling in "coming soon" links

Each placeholder in `index.html` is marked with a `TODO` comment, and the matching cells in the **Resources** table read
"Coming soon":

| What | Where |
|---|---|
| Belt-Finger code | `TODO: replace with the V1 code repo link` |
| Belt-Finger dataset | `TODO: replace with the V1 dataset link` |
| Belt-Finger-Touch paper | `TODO: replace with the paper link` (also update the BibTeX entry) |

To fill one in, replace the `<span class="btn off" …>…</span>` with an `<a class="btn" href="…">…</a>` like its neighbours.
