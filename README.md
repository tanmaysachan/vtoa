# vtoa

**Video to ASCII** — Convert any video to ASCII art playable in your terminal.
[Fully vibecoded btw]

```
@@@@@@@@@@%%%%%%%%%%%%%@@@@@@@@@
@@@@@@##*+=-:..   ..::-=+*##@@@@
@@@@%#*+=-:.           .:-=+*#%@
@@@%#*+-:.               .:-+*#%
@@%#*+-:                   :-+*#
@%#*+-.       .::::::.       -+*
%#*+-.      .:-======-:.     .-+
#*+-       .:-+*####*+=-:.     -
*+-       .:-+*#%%%%#*+=-:.    .
+-.      .:-+*#%@@@@%#*+=-:.   .
-.      .:-+*#%@@@@@@%#*+-:.    
       .:-+*#%@@@@@@@@%#*+-:.   
```

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install opencv-python numpy
```

## Quick Start

### Command Line

```bash
# Play a video with default settings
vtoa video.mp4

# Specify output width
vtoa video.mp4 --width 120

# Use block characters for denser output
vtoa video.mp4 --preset blocks

# Invert for light terminal backgrounds
vtoa video.mp4 --invert

# Loop continuously
vtoa video.mp4 --loop

# Custom character set
vtoa video.mp4 --chars "@#*+=-. "
```

### Python API

```python
from vtoa import play_video, AsciiPlayer, AsciiConverter
import cv2

# Simple one-liner
play_video("video.mp4")

# With options
play_video(
    "video.mp4",
    width=100,
    invert=True,
    loop=True
)

# Using the player class
player = AsciiPlayer("video.mp4", width=80)
print(f"Duration: {player.duration:.1f}s")
print(f"Frames: {player.frame_count}")
player.play()

# Process frames manually
player = AsciiPlayer("video.mp4")
for frame in player.frames():
    print(frame.content)
    print(f"Timestamp: {frame.timestamp:.2f}s")
    break  # Just show first frame

# Convert a single image/frame
from vtoa import frame_to_ascii
image = cv2.imread("image.jpg")
ascii_art = frame_to_ascii(image, width=60)
print(ascii_art)
```

## Character Presets

| Preset | Characters | Best For |
|--------|------------|----------|
| `detailed` | `@%#*+=-:. ` | General use, good detail |
| `simple` | `@#=-. ` | Faster rendering |
| `blocks` | `█▓▒░ ` | Dense output, block style |

## CLI Options

```
usage: vtoa [-h] [-V] [-w WIDTH] [-H HEIGHT] [-p {detailed,simple,blocks}]
            [-c CHARS] [-i] [-l] [-s] video

positional arguments:
  video                 Path to the video file

options:
  -h, --help            Show this help message and exit
  -V, --version         Show version number and exit
  -w, --width WIDTH     Output width in characters
  -H, --height HEIGHT   Output height in characters
  -p, --preset PRESET   Character preset (detailed/simple/blocks)
  -c, --chars CHARS     Custom character set (dark to light)
  -i, --invert          Invert brightness mapping
  -l, --loop            Loop the video
  -s, --no-status       Hide the status bar
```

## How It Works

1. **Read** — OpenCV reads video frames
2. **Grayscale** — Convert each frame to grayscale
3. **Resize** — Scale to fit terminal dimensions (adjusting for character aspect ratio)
4. **Map** — Map pixel brightness values to ASCII characters
5. **Display** — Render frames with proper timing to maintain video speed

## Requirements

- Python 3.8+
- OpenCV (`opencv-python`)
- NumPy

## License

MIT

