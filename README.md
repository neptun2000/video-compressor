# Video Compressor

A Python script for compressing MOV video files using FFmpeg with advanced compression settings and progress tracking.

## Features

- Compress MOV video files with customizable quality settings
- Support for high compression mode with optimized settings
- Two-pass encoding option for better compression results
- Real-time progress bar during compression
- Handles large video files (4GB+)
- Detailed compression statistics output

## Requirements

- Python 3.x
- FFmpeg

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/video-compressor.git
cd video-compressor
```

2. Install the required Python packages:
```bash
pip install tqdm
```

3. Ensure FFmpeg is installed on your system.

## Usage

Basic compression:
```bash
python video_compressor.py input_video.mov
```

High compression mode:
```bash
python video_compressor.py input_video.mov --high-compression
```

Two-pass encoding (for better compression):
```bash
python video_compressor.py input_video.mov --high-compression --two-pass
```

## Compression Settings

- Default mode: CRF 23, medium preset, 128k audio
- High compression mode: CRF 35, veryslow preset, 64k audio, 720p scaling
- Supports custom quality settings through the VideoCompressor class

## Testing

Run the test suite:
```bash
python -m unittest test_video_compressor.py test_high_compression.py
```

## License

This project is open source and available under the MIT License.
