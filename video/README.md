# 5F Real × AI comparison videos

The video masters are rendered deterministically from the existing WebP source
pairs. They do not download media or depend on a proprietary editor.

## Render

Requirements:

- Python 3 with Pillow
- ffmpeg and ffprobe with libx264

From the repository root:

```bash
python3 video/render.py
python3 video/render_horizontal.py --music /path/to/serene-view.mp3
```

The default outputs are:

`docs/assets/video/5f-real-vs-ai-vertical.mp4`

`docs/assets/video/5f-real-vs-ai-horizontal.mp4`

The horizontal video uses the same animated divider for every scene, including
Room 2B, and preserves each complete 16:9 panorama. The vertical renderer uses
a shared center crop and retains its original Room 2B crossfade treatment.

## Background music

The published horizontal video uses **Serene View** by **Arulo**, downloaded
from Mixkit on 2026-08-19. Mixkit permits its free stock music in YouTube,
websites, social media, and online advertising; attribution is not required.
The source MP3 is intentionally not redistributed in this repository.

- Track: https://mixkit.co/free-stock-music/ (item 443)
- Download source: https://assets.mixkit.co/music/443/443.mp3
- License: https://mixkit.co/license/
- Source SHA-256: `556ae7a19c783bd666593e60fbba776bac7f9ff6c2173bebded0bc200cc82ec3`
