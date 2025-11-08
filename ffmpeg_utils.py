from pathlib import Path

# Map UI preset to encoder preset
# "low" in UI → slower encode (better quality). We'll map to 'slow'.
PRESET_MAP = {
    "medium": "medium",
    "low": "slow",
}

RES_MAP = {
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
}

def guess_container(codec: str, subs: str) -> str:
    # If subs are copied, mp4 often fails. Use mkv instead.
    if subs == "copy":
        return "mkv"
    return "mp4"


def build_ffmpeg_cmd(
    *, input_file: str, output_file: str, codec: str, resolution: str,
    preset: str, crf: int, audio: str, subs: str
):
    h = RES_MAP.get(resolution, 720)

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file,
        # Keep FPS same as source: do not set -r
        "-vf", f"scale=-2:{h}",
    ]

    if codec == "h265":
        cmd += [
            "-c:v", "libx265",
            "-preset", PRESET_MAP.get(preset, "medium"),
            "-crf", str(crf),
            "-x265-params", "profile=main10:level=4.0",
        ]
    else:
        # h264 fallback
        cmd += [
            "-c:v", "libx264",
            "-preset", PRESET_MAP.get(preset, "medium"),
            "-crf", str(crf),
            "-profile:v", "high",
            "-level:v", "4.0",
        ]

    # Audio handling
    if audio == "copy":
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-an"]  # no audio

    # Subtitles handling
    if subs == "copy":
        cmd += ["-c:s", "copy"]
    else:
        cmd += ["-sn"]  # drop subs

    cmd += [output_file]
    return cmd


def human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

