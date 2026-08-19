#!/usr/bin/env python3
"""Render the 5F real-vs-AI vertical social video.

Requires Python 3, Pillow, and ffmpeg/ffprobe on PATH. The render is silent by
design because the repository does not contain licensed music.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH = 1080
HEIGHT = 1920
FPS = 30

NORMAL_DURATION = 3.4
REAL_HOLD = 0.8
REVEAL_DURATION = 1.8
SPECIAL_DURATION = 3.2
INTRO_DURATION = 1.2
OUTRO_DURATION = 1.8

OFF_WHITE = "#EEE8DC"
CHARCOAL = "#1D1C19"
ACCENT = "#B68B55"

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = REPO_ROOT / "docs/assets/images/webp/1600"
DEFAULT_OUTPUT = REPO_ROOT / "docs/assets/video/5f-real-vs-ai-vertical.mp4"


@dataclass(frozen=True)
class Scene:
    title: str
    subtitle: str
    real: str
    ai: str
    mode: str = "slider"
    focus_x: float = 0.5


SCENES = [
    Scene(
        "客廳 A",
        "溫暖木質感",
        "5f-living-view-07.webp",
        "5f-ai-staging-living-01.webp",
    ),
    Scene(
        "客廳 B",
        "簡約柔和",
        "5f-living-view-02.webp",
        "5f-ai-staging-living-02.webp",
    ),
    Scene(
        "餐廚",
        "完整餐桌配置",
        "5f-dining-kitchen-view-01.webp",
        "5f-ai-staging-dining-kitchen.webp",
    ),
    Scene(
        "房間 1",
        "舒適臥室",
        "5f-bedroom-1-view-01.webp",
        "5f-ai-staging-bedroom-1.webp",
    ),
    Scene(
        "房間 2A",
        "雙人配置",
        "5f-bedroom-2-view-03.webp",
        "5f-ai-staging-bedroom-2-01.webp",
    ),
    Scene(
        "房間 2B",
        "單人房想像",
        "5f-bedroom-2-view-01.webp",
        "5f-ai-staging-bedroom-2-02.webp",
        mode="crossfade",
    ),
    Scene(
        "第三房｜臥室",
        "客房／第三臥室",
        "5f-bedroom-3-builtins.webp",
        "5f-ai-staging-bedroom-3-bed.webp",
    ),
    Scene(
        "第三房｜兒童房",
        "Montessori 想像",
        "5f-bedroom-3-builtins.webp",
        "5f-ai-staging-bedroom-3-kids.webp",
    ),
    Scene(
        "第三房｜工作室",
        "電腦工作空間",
        "5f-bedroom-3-builtins.webp",
        "5f-ai-staging-bedroom-3-office.webp",
    ),
]


def find_font() -> Path:
    candidates = [
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No suitable CJK-capable font was found.")


FONT_PATH = find_font()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def require_tools() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("ffmpeg and ffprobe must be available on PATH.")
    missing = [name for scene in SCENES for name in (scene.real, scene.ai) if not (ASSET_ROOT / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing source assets: {', '.join(sorted(set(missing)))}")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def common_vertical_crop(real_path: Path, ai_path: Path, focus_x: float) -> tuple[Image.Image, Image.Image]:
    """Apply the same normalized geometry to both halves of an aligned pair."""
    real = Image.open(real_path).convert("RGB")
    ai = Image.open(ai_path).convert("RGB")
    ai = ai.resize(real.size, Image.Resampling.LANCZOS)
    centering = (focus_x, 0.5)
    return (
        ImageOps.fit(real, (WIDTH, HEIGHT), Image.Resampling.LANCZOS, centering=centering),
        ImageOps.fit(ai, (WIDTH, HEIGHT), Image.Resampling.LANCZOS, centering=centering),
    )


def independent_vertical_crop(path: Path, focus_x: float) -> Image.Image:
    source = Image.open(path).convert("RGB")
    return ImageOps.fit(
        source,
        (WIDTH, HEIGHT),
        Image.Resampling.LANCZOS,
        centering=(focus_x, 0.5),
    )


def add_vertical_gradient(layer: Image.Image, *, top: bool) -> None:
    draw = ImageDraw.Draw(layer)
    span = 390 if top else 360
    for offset in range(span):
        strength = 172 if top else 150
        alpha = int(strength * (1.0 - offset / span) ** 1.8)
        y = offset if top else HEIGHT - 1 - offset
        draw.line((0, y, WIDTH, y), fill=(16, 15, 13, alpha))


def rounded_label(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    *,
    fill: tuple[int, int, int, int],
    text_fill: tuple[int, int, int, int],
    anchor: str = "la",
) -> None:
    x, y = position
    box = draw.textbbox((x, y), text, font=text_font, anchor=anchor)
    pad_x, pad_y = 22, 13
    background = (box[0] - pad_x, box[1] - pad_y, box[2] + pad_x, box[3] + pad_y)
    draw.rounded_rectangle(background, radius=24, fill=fill)
    draw.text((x, y), text, font=text_font, fill=text_fill, anchor=anchor)


def make_scene_ui(scene: Scene, index: int) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    add_vertical_gradient(layer, top=True)
    add_vertical_gradient(layer, top=False)
    draw = ImageDraw.Draw(layer)

    draw.text((52, 72), scene.title, font=font(64), fill=(248, 245, 238, 255), anchor="la")
    draw.text((54, 137), scene.subtitle, font=font(29), fill=(244, 239, 230, 220), anchor="la")
    draw.text(
        (WIDTH - 52, 83),
        f"{index:02d} / {len(SCENES):02d}",
        font=font(25),
        fill=(244, 239, 230, 220),
        anchor="ra",
    )

    rounded_label(
        draw,
        (54, 218),
        "真實屋況",
        font(28),
        fill=(238, 232, 220, 235),
        text_fill=(28, 27, 24, 255),
    )
    rounded_label(
        draw,
        (WIDTH - 54, 218),
        "AI 軟裝示意",
        font(28),
        fill=(29, 28, 25, 225),
        text_fill=(248, 245, 238, 255),
        anchor="ra",
    )

    draw.text(
        (54, HEIGHT - 74),
        "南勢角 5F｜真實屋況 × AI 軟裝示意",
        font=font(25),
        fill=(248, 245, 238, 230),
        anchor="ld",
    )

    if scene.mode == "crossfade":
        rounded_label(
            draw,
            (WIDTH // 2, HEIGHT - 156),
            "AI 構圖略有偏移｜以淡入呈現",
            font(25),
            fill=(29, 28, 25, 220),
            text_fill=(248, 245, 238, 255),
            anchor="ma",
        )
    return layer


def make_divider() -> Image.Image:
    divider = Image.new("RGBA", (72, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(divider)
    center_x = divider.width // 2
    center_y = HEIGHT // 2
    draw.line((center_x + 2, 0, center_x + 2, HEIGHT), fill=(0, 0, 0, 80), width=7)
    draw.line((center_x, 0, center_x, HEIGHT), fill=(255, 255, 255, 245), width=4)
    draw.ellipse(
        (center_x - 34, center_y - 34, center_x + 34, center_y + 34),
        fill=(248, 245, 238, 250),
        outline=(29, 28, 25, 100),
        width=2,
    )
    draw.polygon(
        [(center_x - 18, center_y), (center_x - 7, center_y - 10), (center_x - 7, center_y + 10)],
        fill=(29, 28, 25, 230),
    )
    draw.polygon(
        [(center_x + 18, center_y), (center_x + 7, center_y - 10), (center_x + 7, center_y + 10)],
        fill=(29, 28, 25, 230),
    )
    return divider


def centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, size: int, fill: str) -> None:
    draw.text((WIDTH // 2, y), text, font=font(size), fill=fill, anchor="ma")


def make_intro() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), OFF_WHITE)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((410, 500, 670, 562), radius=31, fill=CHARCOAL)
    centered_text(draw, 531, "南勢角 5F", 27, OFF_WHITE)
    centered_text(draw, 748, "同一個家，", 72, CHARCOAL)
    centered_text(draw, 842, "可以有很多種生活", 72, CHARCOAL)
    draw.line((230, 955, 850, 955), fill=ACCENT, width=3)
    centered_text(draw, 1018, "真實屋況 × AI 軟裝示意", 34, "#555149")
    centered_text(draw, 1618, "3房2衛｜可貓｜屋主自租", 28, "#6A655C")
    return image


def make_outro() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), CHARCOAL)
    draw = ImageDraw.Draw(image)
    draw.ellipse((WIDTH // 2 - 7, 586, WIDTH // 2 + 7, 600), fill=ACCENT)
    centered_text(draw, 730, "喜歡這個家？", 74, OFF_WHITE)
    centered_text(draw, 834, "預約現場看房", 74, OFF_WHITE)
    draw.line((270, 964, 810, 964), fill=ACCENT, width=3)
    centered_text(draw, 1035, "南勢角｜3房2衛｜可貓｜屋主自租", 30, "#D8D0C3")
    centered_text(draw, 1640, "真實屋況，現場確認最準確", 25, "#AFA89E")
    return image


def encoder_args(crf: int) -> list[str]:
    return [
        "-an",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        str(crf),
        "-profile:v",
        "high",
        "-level",
        "4.2",
        "-pix_fmt",
        "yuv420p",
        "-g",
        str(FPS * 2),
        "-keyint_min",
        str(FPS * 2),
        "-sc_threshold",
        "0",
        "-video_track_timescale",
        "30000",
    ]


def render_still(source: Path, output: Path, duration: float, crf: int) -> None:
    fade_out = duration - 0.25
    filters = (
        f"fade=t=in:st=0:d=0.16:color=0x{CHARCOAL[1:]},"
        f"fade=t=out:st={fade_out}:d=0.25:color=0x{CHARCOAL[1:]},format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-stats",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(source),
            "-vf",
            filters,
            "-t",
            str(duration),
            *encoder_args(crf),
            str(output),
        ]
    )


def render_slider_scene(
    real: Path,
    ai: Path,
    ui: Path,
    divider: Path,
    output: Path,
    crf: int,
) -> None:
    fade_out = NORMAL_DURATION - 0.25
    progress = f"clip((T-{REAL_HOLD})/{REVEAL_DURATION},0,1)"
    divider_x = f"W*clip((t-{REAL_HOLD})/{REVEAL_DURATION},0,1)-w/2"
    filters = (
        f"[0:v]trim=duration={NORMAL_DURATION},setpts=PTS-STARTPTS,format=rgba[real];"
        f"[1:v]trim=duration={NORMAL_DURATION},setpts=PTS-STARTPTS,format=rgba[ai];"
        f"[real][ai]blend=all_expr='if(lte(X,W*{progress}),B,A)'[mix];"
        f"[2:v]trim=duration={NORMAL_DURATION},setpts=PTS-STARTPTS,format=rgba[ui];"
        f"[mix][ui]overlay=x=0:y=0:shortest=1[with_ui];"
        f"[3:v]trim=duration={NORMAL_DURATION},setpts=PTS-STARTPTS,format=rgba[divider];"
        f"[with_ui][divider]overlay=x='{divider_x}':y=0:shortest=1,"
        f"fade=t=in:st=0:d=0.12:color=0x{CHARCOAL[1:]},"
        f"fade=t=out:st={fade_out}:d=0.25:color=0x{CHARCOAL[1:]},"
        "format=yuv420p[out]"
    )
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y"]
    for source in (real, ai, ui, divider):
        command.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(source)])
    command.extend(
        [
            "-filter_complex",
            filters,
            "-map",
            "[out]",
            "-t",
            str(NORMAL_DURATION),
            *encoder_args(crf),
            str(output),
        ]
    )
    run(command)


def render_crossfade_scene(real: Path, ai: Path, ui: Path, output: Path, crf: int) -> None:
    real_hold = 1.2
    crossfade = 0.6
    ai_hold = 1.4
    real_duration = real_hold + crossfade
    ai_duration = crossfade + ai_hold
    fade_out = SPECIAL_DURATION - 0.25
    filters = (
        f"[0:v]trim=duration={real_duration},setpts=PTS-STARTPTS,format=rgba[real];"
        f"[1:v]trim=duration={ai_duration},setpts=PTS-STARTPTS,format=rgba[ai];"
        f"[real][ai]xfade=transition=fade:duration={crossfade}:offset={real_hold}[mix];"
        f"[2:v]trim=duration={SPECIAL_DURATION},setpts=PTS-STARTPTS,format=rgba[ui];"
        f"[mix][ui]overlay=x=0:y=0:shortest=1,"
        f"fade=t=in:st=0:d=0.12:color=0x{CHARCOAL[1:]},"
        f"fade=t=out:st={fade_out}:d=0.25:color=0x{CHARCOAL[1:]},"
        "format=yuv420p[out]"
    )
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y"]
    for source in (real, ai, ui):
        command.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(source)])
    command.extend(
        [
            "-filter_complex",
            filters,
            "-map",
            "[out]",
            "-t",
            str(SPECIAL_DURATION),
            *encoder_args(crf),
            str(output),
        ]
    )
    run(command)


def probe(path: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_name,width,height,r_frame_rate,pix_fmt",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def render(output: Path, crf: int) -> None:
    require_tools()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="testing-591-video-") as temporary:
        work = Path(temporary)
        segments: list[Path] = []

        intro = work / "intro.png"
        make_intro().save(intro)
        intro_segment = work / "segment-00.mp4"
        print("[01/12] Rendering intro", flush=True)
        render_still(intro, intro_segment, INTRO_DURATION, crf)
        segments.append(intro_segment)

        divider = work / "divider.png"
        make_divider().save(divider)

        for index, scene in enumerate(SCENES, start=1):
            real_path = ASSET_ROOT / scene.real
            ai_path = ASSET_ROOT / scene.ai

            if scene.mode == "slider":
                real_image, ai_image = common_vertical_crop(real_path, ai_path, scene.focus_x)
            else:
                real_image = independent_vertical_crop(real_path, scene.focus_x)
                ai_image = independent_vertical_crop(ai_path, scene.focus_x)

            real_frame = work / f"scene-{index:02d}-real.png"
            ai_frame = work / f"scene-{index:02d}-ai.png"
            ui_frame = work / f"scene-{index:02d}-ui.png"
            real_image.save(real_frame, optimize=True)
            ai_image.save(ai_frame, optimize=True)
            make_scene_ui(scene, index).save(ui_frame, optimize=True)

            segment = work / f"segment-{index:02d}.mp4"
            treatment = "crossfade" if scene.mode == "crossfade" else "slider"
            print(f"[{index + 1:02d}/12] Rendering {scene.title} ({treatment})", flush=True)
            if scene.mode == "crossfade":
                render_crossfade_scene(real_frame, ai_frame, ui_frame, segment, crf)
            else:
                render_slider_scene(real_frame, ai_frame, ui_frame, divider, segment, crf)
            segments.append(segment)

        outro = work / "outro.png"
        make_outro().save(outro)
        outro_segment = work / "segment-10.mp4"
        print("[11/12] Rendering outro", flush=True)
        render_still(outro, outro_segment, OUTRO_DURATION, crf)
        segments.append(outro_segment)

        concat_file = work / "segments.txt"
        concat_file.write_text(
            "".join(f"file '{segment.as_posix()}'\n" for segment in segments),
            encoding="utf-8",
        )
        temporary_output = output.with_suffix(".rendering.mp4")
        print("[12/12] Joining and optimizing MP4", flush=True)
        run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-stats",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(temporary_output),
            ]
        )
        os.replace(temporary_output, output)

    metadata = probe(output)
    duration = float(metadata["format"]["duration"])
    size = int(metadata["format"]["size"])
    print(f"Rendered: {output}")
    print(f"Duration: {duration:.2f}s")
    print(f"Size: {size / 1024 / 1024:.2f} MiB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--crf", type=int, default=20, choices=range(16, 29))
    args = parser.parse_args()
    render(args.output.resolve(), args.crf)


if __name__ == "__main__":
    main()
