"""
Core ASCII conversion logic for video frames.
"""

import shutil
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np

# ASCII characters ordered by visual density (dark to light)
ASCII_CHARS_DETAILED = "@%#*+=-:. "
ASCII_CHARS_SIMPLE = "@#=-. "
ASCII_CHARS_BLOCKS = "█▓▒░ "

# Common aspect ratios (width:height)
ASPECT_RATIO_REEL = 9 / 16  # Instagram Reels, YouTube Shorts (vertical)
ASPECT_RATIO_VIDEO = 16 / 9  # Standard YouTube videos (horizontal)
ASPECT_RATIO_SQUARE = 1.0  # Square videos

# ANSI escape codes
ANSI_RESET = "\033[0m"


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI 24-bit true color foreground escape code."""
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_ansi_bg(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI 24-bit true color background escape code."""
    return f"\033[48;2;{r};{g};{b}m"


@dataclass
class AsciiFrame:
    """Represents a single ASCII frame."""

    content: str
    width: int
    height: int
    timestamp: float


class AsciiConverter:
    """
    Converts video frames to ASCII art.

    Args:
        chars: ASCII character set to use (dark to light).
        width: Target width in characters. If None, auto-calculated.
        height: Target height in characters. If None, auto-calculated.
        aspect_ratio: Force a specific aspect ratio (width/height). 
                      E.g., 9/16 for vertical reels, 16/9 for horizontal videos.
                      If None, uses the video's native aspect ratio.
        invert: If True, inverts the brightness mapping.
        color: If True, outputs colored ASCII using ANSI escape codes.
    """

    # Terminal characters are roughly 2x taller than wide
    CHAR_ASPECT_RATIO = 0.5

    def __init__(
        self,
        chars: str = ASCII_CHARS_DETAILED,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect_ratio: Optional[float] = None,
        invert: bool = False,
        color: bool = False,
    ):
        self.chars = chars if not invert else chars[::-1]
        self.width = width
        self.height = height
        self.aspect_ratio = aspect_ratio
        self.color = color
        self._char_count = len(self.chars)

    def get_terminal_size(self) -> Tuple[int, int]:
        """Get the current terminal dimensions."""
        size = shutil.get_terminal_size((80, 24))
        # Reserve 1 line for status bar
        return size.columns, size.lines - 1

    def calculate_dimensions(
        self, frame_width: int, frame_height: int
    ) -> Tuple[int, int]:
        """
        Calculate output dimensions maintaining aspect ratio.

        If aspect_ratio is set, uses that instead of the frame's native ratio.
        Fits the result within terminal bounds.
        """
        term_width, term_height = self.get_terminal_size()

        # Determine the aspect ratio to use
        if self.aspect_ratio is not None:
            aspect_ratio = self.aspect_ratio
        else:
            aspect_ratio = frame_width / frame_height

        # If both dimensions specified, use them directly
        if self.width is not None and self.height is not None:
            return min(self.width, term_width), min(self.height, term_height)

        # Calculate dimensions to fit within terminal while maintaining aspect ratio
        # Account for character aspect ratio (chars are ~2x taller than wide)
        char_adjusted_ratio = aspect_ratio / self.CHAR_ASPECT_RATIO

        if self.width is not None:
            # Width specified, calculate height
            target_width = min(self.width, term_width)
            target_height = int(target_width / char_adjusted_ratio)
        elif self.height is not None:
            # Height specified, calculate width
            target_height = min(self.height, term_height)
            target_width = int(target_height * char_adjusted_ratio)
        else:
            # Neither specified - fit to terminal
            # Try fitting by width first
            target_width = term_width
            target_height = int(target_width / char_adjusted_ratio)

            # If height exceeds terminal, fit by height instead
            if target_height > term_height:
                target_height = term_height
                target_width = int(target_height * char_adjusted_ratio)

        # Final bounds check
        target_width = max(1, min(target_width, term_width))
        target_height = max(1, min(target_height, term_height))

        return target_width, target_height

    def frame_to_ascii(
        self,
        frame: np.ndarray,
        timestamp: float = 0.0,
    ) -> AsciiFrame:
        """
        Convert a single video frame to ASCII art.

        Args:
            frame: BGR or grayscale numpy array from OpenCV.
            timestamp: Frame timestamp in seconds.

        Returns:
            AsciiFrame containing the ASCII representation.
        """
        # Get original dimensions
        if len(frame.shape) == 3:
            original_height, original_width = frame.shape[:2]
        else:
            original_height, original_width = frame.shape

        # Calculate target dimensions
        target_width, target_height = self.calculate_dimensions(
            original_width, original_height
        )

        # Convert to grayscale for character mapping
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Resize grayscale for character selection
        resized_gray = cv2.resize(
            gray,
            (target_width, target_height),
            interpolation=cv2.INTER_AREA,
        )

        # Map pixel values to ASCII character indices
        indices = (resized_gray / 255 * (self._char_count - 1)).astype(np.uint8)

        if self.color and len(frame.shape) == 3:
            # Resize color frame for color extraction
            resized_color = cv2.resize(
                frame,
                (target_width, target_height),
                interpolation=cv2.INTER_AREA,
            )
            # Convert BGR to RGB
            resized_rgb = cv2.cvtColor(resized_color, cv2.COLOR_BGR2RGB)

            # Build colored ASCII string
            lines = []
            for y in range(target_height):
                line_chars = []
                for x in range(target_width):
                    char = self.chars[indices[y, x]]
                    r, g, b = resized_rgb[y, x]
                    # Apply color to character
                    colored_char = f"{rgb_to_ansi(r, g, b)}{char}"
                    line_chars.append(colored_char)
                # Reset color at end of line
                lines.append("".join(line_chars) + ANSI_RESET)

            content = "\n".join(lines)
        else:
            # Build plain ASCII string (no color)
            lines = []
            for row in indices:
                line = "".join(self.chars[i] for i in row)
                lines.append(line)

            content = "\n".join(lines)

        return AsciiFrame(
            content=content,
            width=target_width,
            height=target_height,
            timestamp=timestamp,
        )


def frame_to_ascii(
    frame: np.ndarray,
    chars: str = ASCII_CHARS_DETAILED,
    width: Optional[int] = None,
    height: Optional[int] = None,
    aspect_ratio: Optional[float] = None,
    invert: bool = False,
    color: bool = False,
) -> str:
    """
    Convenience function to convert a single frame to ASCII.

    Args:
        frame: BGR or grayscale numpy array.
        chars: ASCII character set (dark to light).
        width: Target width in characters.
        height: Target height in characters.
        aspect_ratio: Force a specific aspect ratio (width/height).
        invert: Invert brightness mapping.
        color: Use colored ASCII output.

    Returns:
        ASCII art string.
    """
    converter = AsciiConverter(
        chars=chars,
        width=width,
        height=height,
        aspect_ratio=aspect_ratio,
        invert=invert,
        color=color,
    )
    result = converter.frame_to_ascii(frame)
    return result.content
