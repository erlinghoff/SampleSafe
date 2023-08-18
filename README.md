
# SampleSafe Audio Processing Tool

## Overview
The SampleSafe tool ensures that audio files start and end at zero-crossing points to prevent pops or clicks at the beginning or end of audio tracks. It is designed for audio professionals who require the highest level of quality and precision in their work.

**Note**: The tool intelligently applies fades only when a channel isn't already aligned closely to a zero-crossing point at its start or end.

## Features
- **Support for Multiple Formats**: Handles common audio formats including WAV, MP3, etc.
- **Bit Depth Preservation**: Retains the original bit depth of WAV files.
- **No Unnecessary Re-encodings**: For MP3 files, only the start and end portions are re-encoded to ensure minimal quality loss. The main body remains untouched.

## Installation

### Dependencies

1. **FFmpeg**:
   - **Ubuntu/Debian**: 
     ```
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **macOS** (using Homebrew):
     ```
     brew install ffmpeg
     ```
   - **Windows**: Download the binaries from the [official FFmpeg site](https://ffmpeg.org/download.html) and add the path to `ffmpeg.exe` to your system's PATH variable.

2. **Python Libraries**: After installing FFmpeg, you can install the required Python libraries using:
   ```
   pip install -r requirements.txt
   ```

## Usage
```bash
$ python samplesafe.py [input_file] [-v]
```
- `input_file`: Path to the audio file you want to process.
- `-v`: Enable verbose mode to view detailed logs of the processing steps.

## Verbose Mode
In verbose mode, the tool provides detailed insights into each step of the processing:
- File details and properties being processed.
- Reasons for actions taken.
- Actual actions being performed.

## Why Zero-Crossing Points Matter?
Starting or ending an audio file at non-zero crossing points can introduce pops or clicks. This is because the audio waveform is abruptly interrupted, causing a discontinuity. By ensuring that audio files start and end at zero-crossing points, we can achieve smoother transitions and avoid these audio artifacts.

---

**Note**: This tool is designed with audio professionals in mind. Always backup your original files before processing.
