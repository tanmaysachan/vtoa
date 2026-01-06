"""
Command-line interface for vtoa.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from vtoa import __version__
from vtoa.converter import (
    ASCII_CHARS_BLOCKS,
    ASCII_CHARS_DETAILED,
    ASCII_CHARS_SIMPLE,
    ASPECT_RATIO_REEL,
    ASPECT_RATIO_VIDEO,
)
from vtoa.player import AsciiPlayer

CHAR_PRESETS = {
    "detailed": ASCII_CHARS_DETAILED,
    "simple": ASCII_CHARS_SIMPLE,
    "blocks": ASCII_CHARS_BLOCKS,
}

# URL patterns for detection
URL_PATTERNS = [
    r"^https?://",
    r"^www\.",
]

# Platform detection patterns
INSTAGRAM_PATTERNS = [
    r"instagram\.com/reel",
    r"instagram\.com/reels",
    r"instagram\.com/p/",
]

YOUTUBE_SHORTS_PATTERNS = [
    r"youtube\.com/shorts",
    r"youtu\.be/.*#shorts",
]

YOUTUBE_PATTERNS = [
    r"youtube\.com/watch",
    r"youtu\.be/",
    r"youtube\.com/v/",
]


def is_url(source: str) -> bool:
    """Check if the source is a URL."""
    for pattern in URL_PATTERNS:
        if re.match(pattern, source, re.IGNORECASE):
            return True
    return False


def detect_aspect_ratio(url: str) -> float | None:
    """
    Detect the appropriate aspect ratio based on the URL.

    Returns:
        Aspect ratio (width/height) or None to use video's native ratio.
    """
    url_lower = url.lower()

    # Instagram Reels - vertical 9:16
    for pattern in INSTAGRAM_PATTERNS:
        if re.search(pattern, url_lower):
            return ASPECT_RATIO_REEL

    # YouTube Shorts - vertical 9:16
    for pattern in YOUTUBE_SHORTS_PATTERNS:
        if re.search(pattern, url_lower):
            return ASPECT_RATIO_REEL

    # Regular YouTube - horizontal 16:9
    for pattern in YOUTUBE_PATTERNS:
        if re.search(pattern, url_lower):
            return ASPECT_RATIO_VIDEO

    # Unknown - use native aspect ratio
    return None


def download_video(url: str, output_path: Path) -> bool:
    """
    Download video from URL using yt-dlp.

    Args:
        url: Video URL (YouTube, Instagram, etc.)
        output_path: Path to save the downloaded video.

    Returns:
        True if download succeeded, False otherwise.
    """
    print(f"Downloading: {url}")
    print("This may take a moment...")

    try:
        result = subprocess.run(
            ["yt-dlp", url, "-o", str(output_path), "--no-playlist", "-q", "--progress"],
            capture_output=False,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: yt-dlp is not installed.", file=sys.stderr)
        print("Install it with: pip install yt-dlp", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error downloading video: {e}", file=sys.stderr)
        return False


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="vtoa",
        description="Convert and play videos as ASCII art in your terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vtoa video.mp4                              Play local video
  vtoa https://youtube.com/watch?v=xxx        Play YouTube video (16:9)
  vtoa https://youtube.com/shorts/xxx         Play YouTube Short (9:16)
  vtoa https://instagram.com/reel/xxx         Play Instagram reel (9:16)
  vtoa video.mp4 --aspect 16:9                Force 16:9 aspect ratio
  vtoa video.mp4 --aspect 9:16                Force 9:16 vertical ratio
  vtoa video.mp4 --width 120                  Play with specific width
  vtoa video.mp4 --preset blocks              Use block characters
  vtoa video.mp4 --invert                     Invert brightness
  vtoa video.mp4 --color                      Enable colored output
  vtoa video.mp4 --loop                       Loop the video
        """,
    )

    parser.add_argument(
        "source",
        type=str,
        help="Path to video file OR URL (YouTube, Instagram, etc.)",
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"vtoa {__version__}",
    )

    parser.add_argument(
        "-w", "--width",
        type=int,
        default=None,
        help="Output width in characters (default: auto)",
    )

    parser.add_argument(
        "-H", "--height",
        type=int,
        default=None,
        help="Output height in characters (default: auto)",
    )

    parser.add_argument(
        "-a", "--aspect",
        type=str,
        default=None,
        help="Force aspect ratio as W:H (e.g., 16:9, 9:16, 1:1). Auto-detected for URLs.",
    )

    parser.add_argument(
        "-p", "--preset",
        choices=list(CHAR_PRESETS.keys()),
        default="detailed",
        help="Character preset: detailed, simple, or blocks (default: detailed)",
    )

    parser.add_argument(
        "-c", "--chars",
        type=str,
        default=None,
        help="Custom character set (dark to light). Overrides --preset",
    )

    parser.add_argument(
        "-i", "--invert",
        action="store_true",
        help="Invert brightness mapping (useful for light terminals)",
    )

    parser.add_argument(
        "-C", "--color",
        action="store_true",
        help="Enable colored ASCII output (requires true color terminal)",
    )

    parser.add_argument(
        "-l", "--loop",
        action="store_true",
        help="Loop the video continuously",
    )

    parser.add_argument(
        "-s", "--no-status",
        action="store_true",
        help="Hide the status bar",
    )

    return parser


def parse_aspect_ratio(aspect_str: str) -> float:
    """
    Parse aspect ratio string like '16:9' or '9:16' to float.

    Returns:
        Aspect ratio as width/height.
    """
    try:
        if ":" in aspect_str:
            w, h = aspect_str.split(":")
            return float(w) / float(h)
        else:
            return float(aspect_str)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"Invalid aspect ratio: {aspect_str}. Use format W:H (e.g., 16:9)")


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    opts = parser.parse_args(args)

    source = opts.source
    video_path: Path
    temp_file: Path | None = None
    aspect_ratio: float | None = None

    # Check if source is a URL or local file
    if is_url(source):
        # Auto-detect aspect ratio from URL
        aspect_ratio = detect_aspect_ratio(source)
        platform = "Instagram Reel" if "instagram" in source.lower() else \
                   "YouTube Short" if "shorts" in source.lower() else \
                   "YouTube" if "youtube" in source.lower() or "youtu.be" in source.lower() else \
                   "Video"
        
        if aspect_ratio == ASPECT_RATIO_REEL:
            print(f"Detected: {platform} (9:16 vertical)")
        elif aspect_ratio == ASPECT_RATIO_VIDEO:
            print(f"Detected: {platform} (16:9 horizontal)")
        else:
            print(f"Detected: {platform}")

        # Download video to temp file
        temp_dir = tempfile.gettempdir()
        temp_file = Path(temp_dir) / "vtoa_download.mp4"

        if not download_video(source, temp_file):
            return 1

        if not temp_file.exists():
            print("Error: Download failed - no video file created.", file=sys.stderr)
            return 1

        video_path = temp_file
        print(f"Downloaded to: {temp_file}\n")
    else:
        # Local file
        video_path = Path(source)
        if not video_path.exists():
            print(f"Error: Video file not found: {video_path}", file=sys.stderr)
            return 1

    # Override aspect ratio if specified via CLI
    if opts.aspect:
        try:
            aspect_ratio = parse_aspect_ratio(opts.aspect)
            print(f"Using aspect ratio: {opts.aspect}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Determine character set
    chars = opts.chars if opts.chars else CHAR_PRESETS[opts.preset]

    try:
        player = AsciiPlayer(
            video_path=video_path,
            chars=chars,
            width=opts.width,
            height=opts.height,
            aspect_ratio=aspect_ratio,
            invert=opts.invert,
            color=opts.color,
            loop=opts.loop,
        )

        print(f"Playing: {source}")
        print(f"Duration: {player.duration:.1f}s | Frames: {player.frame_count} | FPS: {player.fps:.1f}")
        print("Press Ctrl+C to stop\n")

        time.sleep(1)  # Brief pause before starting

        player.play(show_status=not opts.no_status)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nPlayback stopped.")

    finally:
        # Clean up downloaded file
        if temp_file and temp_file.exists():
            try:
                os.remove(temp_file)
                print(f"\nCleaned up: {temp_file}")
            except OSError as e:
                print(f"Warning: Could not delete temp file: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
