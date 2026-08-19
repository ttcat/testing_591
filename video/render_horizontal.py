#!/usr/bin/env python3
"""Render the full-panorama 1920×1080 real-vs-AI comparison video."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from render import (
    ACCENT,
    ASSET_ROOT,
    CHARCOAL,
    FPS,
    OFF_WHITE,
    REPO_ROOT,
    SCENES,
    encoder_args,
    font,
    probe,
    require_tools,
    run,
)


WIDTH = 1920
HEIGHT = 1080

NORMAL_DURATION = 3.4
REAL_HOLD = 0.8
REVEAL_DURATION = 1.8
INTRO_DURATION = 1.2
OUTRO_DURATION = 1.8

DEFAULT_OUTPUT = REPO_ROOT / "docs/assets/video/5f-real-vs-ai-horizontal.mp4"


def full_panorama_pair(real_path: Path, ai_path: Path) -> tuple[Image.Image, Image.Image]:
    """Fit the complete aligned pair without independently cropping either side."""
    real = Image.open(real_path).convert("RGB")
    ai = Image.open(ai_path).convert("RGB").resize(real.size, Image.Resampling.LANCZOS)
    return (
        ImageOps.pad(real, (WIDTH, HEIGHT), Image.Resampling.LANCZOS, color=OFF_WHITE),
        ImageOps.pad(ai, (WIDTH, HEIGHT), Image.Resampling.LANCZOS, color=OFF_WHITE),
    )


def add_gradient(layer: Image.Image, *, top: bool) -> None:
    draw = ImageDraw.Draw(layer)
    span = 245 if top else 190
    for offset in range(span):
        strength = 178 if top else 156
        alpha = int(strength * (1.0 - offset / span) ** 1.7)
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
    pad_x, pad_y = 20, 11
    background = (box[0] - pad_x, box[1] - pad_y, box[2] + pad_x, box[3] + pad_y)
    draw.rounded_rectangle(background, radius=23, fill=fill)
    draw.text((x, y), text, font=text_font, fill=text_fill, anchor=anchor)


def make_scene_ui(scene, index: int) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    add_gradient(layer, top=True)
    add_gradient(layer, top=False)
    draw = ImageDraw.Draw(layer)

    draw.text((64, 42), scene.title, font=font(58), fill=(248, 245, 238, 255), anchor="la")
    draw.text((66, 105), scene.subtitle, font=font(27), fill=(244, 239, 230, 225), anchor="la")
    draw.text(
        (WIDTH - 64, 57),
        f"{index:02d} / {len(SCENES):02d}",
        font=font(27),
        fill=(244, 239, 230, 225),
        anchor="ra",
    )

    rounded_label(
        draw,
        (66, 171),
        "真實屋況",
        font(27),
        fill=(238, 232, 220, 238),
        text_fill=(28, 27, 24, 255),
    )
    rounded_label(
        draw,
        (WIDTH - 66, 171),
        "AI 軟裝示意",
        font(27),
        fill=(29, 28, 25, 228),
        text_fill=(248, 245, 238, 255),
        anchor="ra",
    )

    draw.text(
        (64, HEIGHT - 38),
        "南勢角 5F｜完整全景｜真實屋況 × AI 軟裝示意",
        font=font(24),
        fill=(248, 245, 238, 235),
        anchor="ld",
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
    draw.rounded_rectangle((820, 260, 1100, 322), radius=31, fill=CHARCOAL)
    centered_text(draw, 291, "南勢角 5F", 27, OFF_WHITE)
    centered_text(draw, 460, "同一個家，可以有很多種生活", 72, CHARCOAL)
    draw.line((520, 570, 1400, 570), fill=ACCENT, width=3)
    centered_text(draw, 632, "完整全景｜真實屋況 × AI 軟裝示意", 34, "#555149")
    centered_text(draw, 926, "3房2衛｜可貓｜屋主自租", 28, "#6A655C")
    return image


def make_outro() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), CHARCOAL)
    draw = ImageDraw.Draw(image)
    draw.ellipse((WIDTH // 2 - 7, 256, WIDTH // 2 + 7, 270), fill=ACCENT)
    centered_text(draw, 420, "喜歡這個家？預約現場看房", 68, OFF_WHITE)
    draw.line((600, 538, 1320, 538), fill=ACCENT, width=3)
    centered_text(draw, 610, "南勢角｜3房2衛｜可貓｜屋主自租", 30, "#D8D0C3")
    centered_text(draw, 928, "真實屋況，現場確認最準確", 25, "#AFA89E")
    return image


def render_still(source: Path, output: Path, duration: float, crf: int) -> None:
    filters = (
        f"fade=t=in:st=0:d=0.16:color=0x{CHARCOAL[1:]},"
        f"fade=t=out:st={duration - 0.25}:d=0.25:color=0x{CHARCOAL[1:]},format=yuv420p"
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
        f"fade=t=out:st={NORMAL_DURATION - 0.25}:d=0.25:color=0x{CHARCOAL[1:]},"
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


def add_music(video: Path, music: Path, output: Path) -> None:
    duration = float(probe(video)["format"]["duration"])
    fade_out_start = max(0.0, duration - 1.8)
    filters = (
        f"[1:a]atrim=duration={duration:.3f},asetpts=PTS-STARTPTS,"
        "loudnorm=I=-18:LRA=9:TP=-2,"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out_start:.3f}:d=1.8[audio]"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-stats",
            "-y",
            "-i",
            str(video),
            "-stream_loop",
            "-1",
            "-i",
            str(music),
            "-filter_complex",
            filters,
            "-map",
            "0:v:0",
            "-map",
            "[audio]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            f"{duration:.3f}",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


def render(output: Path, crf: int, music: Path | None) -> None:
    require_tools()
    if music is not None and not music.exists():
        raise FileNotFoundError(f"Music file not found: {music}")
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="testing-591-horizontal-") as temporary:
        work = Path(temporary)
        segments: list[Path] = []

        intro = work / "intro.png"
        make_intro().save(intro)
        intro_segment = work / "segment-00.mp4"
        print("[01/12] Rendering horizontal intro", flush=True)
        render_still(intro, intro_segment, INTRO_DURATION, crf)
        segments.append(intro_segment)

        divider = work / "divider.png"
        make_divider().save(divider)

        for index, scene in enumerate(SCENES, start=1):
            real_path = ASSET_ROOT / scene.real
            ai_path = ASSET_ROOT / scene.ai
            real_image, ai_image = full_panorama_pair(real_path, ai_path)

            real_frame = work / f"scene-{index:02d}-real.png"
            ai_frame = work / f"scene-{index:02d}-ai.png"
            ui_frame = work / f"scene-{index:02d}-ui.png"
            real_image.save(real_frame, optimize=True)
            ai_image.save(ai_frame, optimize=True)
            make_scene_ui(scene, index).save(ui_frame, optimize=True)

            segment = work / f"segment-{index:02d}.mp4"
            print(f"[{index + 1:02d}/12] Rendering {scene.title} (slider, full panorama)", flush=True)
            render_slider_scene(real_frame, ai_frame, ui_frame, divider, segment, crf)
            segments.append(segment)

        outro = work / "outro.png"
        make_outro().save(outro)
        outro_segment = work / "segment-10.mp4"
        print("[11/12] Rendering horizontal outro", flush=True)
        render_still(outro, outro_segment, OUTRO_DURATION, crf)
        segments.append(outro_segment)

        concat_file = work / "segments.txt"
        concat_file.write_text(
            "".join(f"file '{segment.as_posix()}'\n" for segment in segments),
            encoding="utf-8",
        )
        silent_output = output.with_suffix(".silent.mp4")
        print("[12/12] Joining and optimizing horizontal MP4", flush=True)
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
                str(silent_output),
            ]
        )
        if music is None:
            os.replace(silent_output, output)
        else:
            music_output = output.with_suffix(".music.mp4")
            print(f"Adding background music: {music.name}", flush=True)
            add_music(silent_output, music, music_output)
            os.replace(music_output, output)
            silent_output.unlink(missing_ok=True)

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
    parser.add_argument("--music", type=Path, help="Optional licensed background-music file")
    args = parser.parse_args()
    music = args.music.resolve() if args.music else None
    render(args.output.resolve(), args.crf, music)


if __name__ == "__main__":
    main()
