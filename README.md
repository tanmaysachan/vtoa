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

### From PyPI

```bash
pip install vtoa
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/tanmaysachan/vtoa.git
cd vtoa
pip install -e .
```

### Building from Source

To build the package yourself:

```bash
# Install build tools
pip install build

# Build the package
python -m build

# Install the built wheel
pip install dist/vtoa-*.whl
```

## Quick Start

### Command Line

```bash
# Play a local video
vtoa video.mp4

# Play from Instagram Reel URL
vtoa "https://www.instagram.com/reel/xyz123/"

# Enable colored ASCII output
vtoa video.mp4 --color

# Specify output width
vtoa video.mp4 --width 120

# Force aspect ratio (9:16 for reels)
vtoa video.mp4 --aspect 9:16

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
            [-c CHARS] [-a ASPECT] [-C] [-i] [-l] [-s] source

positional arguments:
  source                Video file path or Instagram Reel URL

options:
  -h, --help            Show this help message and exit
  -V, --version         Show version number and exit
  -w, --width WIDTH     Output width in characters
  -H, --height HEIGHT   Output height in characters
  -p, --preset PRESET   Character preset (detailed/simple/blocks)
  -c, --chars CHARS     Custom character set (dark to light)
  -a, --aspect ASPECT   Force aspect ratio (e.g., 16:9, 9:16, 1:1)
  -C, --color           Enable colored ASCII output (requires true color terminal)
  -i, --invert          Invert brightness mapping
  -l, --loop            Loop the video
  -s, --no-status       Hide the status bar
```

## How It Works

1. **Fetch** — Download video from Instagram Reel URL or read local file
2. **Read** — OpenCV reads video frames
3. **Resize** — Scale to fit terminal dimensions (preserving aspect ratio)
4. **Map** — Map pixel brightness values to ASCII characters
5. **Colorize** — Apply ANSI 24-bit true color codes (optional)
6. **Display** — Render frames with proper timing to maintain video speed

## Features

- 🎬 Play local videos or stream from Instagram Reel URLs
- 🎨 Full color support using ANSI 24-bit true color
- 📐 Automatic aspect ratio detection (9:16 for reels)
- ⚡ Smooth playback with frame timing
- 🔧 Customizable character sets and presets
- 🔁 Loop mode for continuous playback

## Requirements

- Python 3.8+
- OpenCV (`opencv-python`)
- NumPy
- yt-dlp (for URL support)

## License

MIT

