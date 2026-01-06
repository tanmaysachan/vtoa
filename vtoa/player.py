"""
Terminal player for ASCII video playback.
"""

import sys
import time
from pathlib import Path
from typing import Callable, Iterator, Optional, Union

import cv2

from vtoa.converter import ASCII_CHARS_DETAILED, AsciiConverter, AsciiFrame


class AsciiPlayer:
    """
    Plays video files as ASCII art in the terminal.

    Args:
        video_path: Path to the video file.
        chars: ASCII character set to use.
        width: Target width in characters.
        height: Target height in characters.
        aspect_ratio: Force a specific aspect ratio (width/height).
        invert: Invert brightness mapping.
        color: Use colored ASCII output.
        loop: Loop the video continuously.
    """

    def __init__(
        self,
        video_path: Union[str, Path],
        chars: str = ASCII_CHARS_DETAILED,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect_ratio: Optional[float] = None,
        invert: bool = False,
        color: bool = False,
        loop: bool = False,
    ):
        self.video_path = Path(video_path)
        self.converter = AsciiConverter(
            chars=chars,
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            invert=invert,
            color=color,
        )
        self.loop = loop
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: float = 30.0
        self._frame_count: int = 0
        self._duration: float = 0.0

    def _open_video(self) -> cv2.VideoCapture:
        """Open the video file and extract metadata."""
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video not found: {self.video_path}")

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {self.video_path}")

        self._fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._duration = self._frame_count / self._fps if self._fps > 0 else 0

        return cap

    @property
    def fps(self) -> float:
        """Video frames per second."""
        return self._fps

    @property
    def frame_count(self) -> int:
        """Total number of frames."""
        return self._frame_count

    @property
    def duration(self) -> float:
        """Video duration in seconds."""
        return self._duration

    def frames(self) -> Iterator[AsciiFrame]:
        """
        Iterate over all frames as ASCII art.

        Yields:
            AsciiFrame for each video frame.
        """
        cap = self._open_video()
        frame_duration = 1.0 / self._fps if self._fps > 0 else 1.0 / 30.0

        try:
            frame_idx = 0
            while True:
                ret, frame = cap.read()

                if not ret:
                    if self.loop:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        frame_idx = 0
                        continue
                    else:
                        break

                timestamp = frame_idx * frame_duration
                ascii_frame = self.converter.frame_to_ascii(frame, timestamp)
                yield ascii_frame
                frame_idx += 1

        finally:
            cap.release()

    def play(
        self,
        show_status: bool = True,
        on_frame: Optional[Callable[[AsciiFrame, int], None]] = None,
    ) -> None:
        """
        Play the video in the terminal.

        Args:
            show_status: Show a status bar with playback info.
            on_frame: Optional callback called for each frame.
        """
        frame_duration = 1.0 / self._fps if self._fps > 0 else 1.0 / 30.0

        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            frame_idx = 0
            for ascii_frame in self.frames():
                start_time = time.perf_counter()

                # Clear screen and move cursor to top-left
                sys.stdout.write("\033[2J\033[H")

                # Write the frame
                sys.stdout.write(ascii_frame.content)

                # Status bar
                if show_status:
                    progress = (
                        (frame_idx + 1) / self._frame_count * 100
                        if self._frame_count > 0
                        else 0
                    )
                    current_time = ascii_frame.timestamp
                    status = (
                        f"\n[{current_time:05.1f}s / {self._duration:05.1f}s] "
                        f"Frame {frame_idx + 1}/{self._frame_count} ({progress:.0f}%)"
                    )
                    sys.stdout.write(status)

                sys.stdout.flush()

                # Call frame callback if provided
                if on_frame:
                    on_frame(ascii_frame, frame_idx)

                frame_idx += 1

                # Maintain target frame rate
                elapsed = time.perf_counter() - start_time
                sleep_time = frame_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            pass

        finally:
            # Show cursor again
            sys.stdout.write("\033[?25h")
            sys.stdout.write("\n")
            sys.stdout.flush()


def play_video(
    video_path: Union[str, Path],
    chars: str = ASCII_CHARS_DETAILED,
    width: Optional[int] = None,
    height: Optional[int] = None,
    aspect_ratio: Optional[float] = None,
    invert: bool = False,
    color: bool = False,
    loop: bool = False,
    show_status: bool = True,
) -> None:
    """
    Convenience function to play a video as ASCII art.

    Args:
        video_path: Path to the video file.
        chars: ASCII character set (dark to light).
        width: Target width in characters.
        height: Target height in characters.
        aspect_ratio: Force a specific aspect ratio (width/height).
        invert: Invert brightness mapping.
        color: Use colored ASCII output.
        loop: Loop the video.
        show_status: Show playback status bar.
    """
    player = AsciiPlayer(
        video_path=video_path,
        chars=chars,
        width=width,
        height=height,
        aspect_ratio=aspect_ratio,
        invert=invert,
        color=color,
        loop=loop,
    )
    player.play(show_status=show_status)
