# 5F Real × AI vertical video

The social-video master is rendered deterministically from the existing WebP
source pairs. It does not download music or depend on a proprietary editor.

## Render

Requirements:

- Python 3 with Pillow
- ffmpeg and ffprobe with libx264

From the repository root:

```bash
python3 video/render.py
python3 video/render_horizontal.py
```

The default outputs are:

`docs/assets/video/5f-real-vs-ai-vertical.mp4`

`docs/assets/video/5f-real-vs-ai-horizontal.mp4`

Room 2B intentionally uses a crossfade because the AI image has composition
drift. Every other scene uses an animated divider. The vertical renderer uses
a shared center crop; the horizontal renderer preserves each complete 16:9
panorama instead.
