#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from typing import Tuple, Optional

class VideoCompressor:
    def __init__(self):
        self.check_ffmpeg()

    def check_ffmpeg(self) -> None:
        """Check if FFmpeg is installed on the system."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
        except FileNotFoundError:
            print("Error: FFmpeg is not installed. Please install FFmpeg to use this script.")
            sys.exit(1)

    def validate_input_file(self, input_path: str) -> bool:
        """
        Validate if the input file exists and is a .mov file.
        
        Args:
            input_path: Path to the input video file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not os.path.exists(input_path):
            print(f"Error: File '{input_path}' not found.")
            return False
        
        if not input_path.lower().endswith('.mov'):
            print("Error: Input file must be a .mov file.")
            return False
            
        return True

    def get_output_path(self, input_path: str) -> str:
        """
        Generate output filename by adding '_compressed' suffix.
        
        Args:
            input_path: Path to the input video file
            
        Returns:
            str: Path for the output compressed file
        """
        base_path = os.path.splitext(input_path)[0]
        return f"{base_path}_compressed.mov"

    def get_video_duration(self, input_path: str) -> Optional[float]:
        """
        Get video duration in seconds using FFprobe.
        
        Args:
            input_path: Path to the input video file
            
        Returns:
            float: Duration in seconds or None if unable to determine
        """
        try:
            cmd = [
                'ffprobe', 
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return None

    def compress_video(self, input_path: str) -> bool:
        """
        Compress the video file using FFmpeg.
        
        Args:
            input_path: Path to the input video file
            
        Returns:
            bool: True if compression was successful, False otherwise
        """
        if not self.validate_input_file(input_path):
            return False

        output_path = self.get_output_path(input_path)
        duration = self.get_video_duration(input_path)

        # FFmpeg compression command with good quality preservation
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'h264',           # Use H.264 codec
            '-crf', '23',             # Constant Rate Factor (18-28 is good)
            '-preset', 'medium',       # Compression preset
            '-c:a', 'aac',            # Audio codec
            '-b:a', '128k',           # Audio bitrate
            '-y',                     # Overwrite output file
            output_path
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            print("\nCompressing video...")
            start_time = time.time()

            # Show progress
            while process.poll() is None:
                print("⏳ Processing... ", end='\r')
                time.sleep(0.5)
                print("⚡ Processing... ", end='\r')
                time.sleep(0.5)

            process.wait()

            if process.returncode == 0:
                end_time = time.time()
                input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
                output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                
                print("\n✅ Compression completed successfully!")
                print(f"Time taken: {end_time - start_time:.2f} seconds")
                print(f"Input size: {input_size:.2f} MB")
                print(f"Output size: {output_size:.2f} MB")
                print(f"Size reduction: {((input_size - output_size) / input_size * 100):.2f}%")
                print(f"Output saved as: {output_path}")
                return True
            else:
                print("\n❌ Error during compression:")
                print(process.stderr.read())
                return False

        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python video_compressor.py <input_video.mov>")
        sys.exit(1)

    compressor = VideoCompressor()
    success = compressor.compress_video(sys.argv[1])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
