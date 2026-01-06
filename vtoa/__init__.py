"""
vtoa - Video to ASCII

Convert any video to ASCII art playable in your terminal.
"""

from vtoa.converter import (
    ASPECT_RATIO_REEL,
    ASPECT_RATIO_VIDEO,
    AsciiConverter,
    frame_to_ascii,
)
from vtoa.player import AsciiPlayer, play_video

__version__ = "0.1.0"
__all__ = [
    "AsciiConverter",
    "AsciiPlayer",
    "frame_to_ascii",
    "play_video",
    "ASPECT_RATIO_REEL",
    "ASPECT_RATIO_VIDEO",
]

