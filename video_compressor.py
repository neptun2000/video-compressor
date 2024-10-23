#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from typing import Tuple, Optional, Dict, Union
from tqdm import tqdm

class VideoCompressor:
    VALID_PRESETS = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
    
    def __init__(self):
        self.check_ffmpeg()

    def check_ffmpeg(self) -> None:
        """Check if FFmpeg is installed on the system."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
        except FileNotFoundError:
            print("Error: FFmpeg is not installed. Please install FFmpeg to use this script.")
            sys.exit(1)

    # ... [rest of the file content remains the same] ...
