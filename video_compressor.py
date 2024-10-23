#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from typing import Tuple, Optional, Dict, Union

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

    def validate_quality_settings(self, settings: Dict[str, Union[int, str, float]]) -> Tuple[bool, str]:
        """
        Validate compression quality settings.
        
        Args:
            settings: Dictionary containing quality settings
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if 'crf' in settings:
            crf = settings['crf']
            if not isinstance(crf, (int, float)) or crf < 0 or crf > 51:
                return False, "CRF must be between 0 and 51 (lower is better quality)"

        if 'preset' in settings:
            preset = settings['preset']
            if preset not in self.VALID_PRESETS:
                return False, f"Preset must be one of: {', '.join(self.VALID_PRESETS)}"

        if 'audio_bitrate' in settings:
            bitrate = settings['audio_bitrate']
            if not isinstance(bitrate, (int, str)) or (isinstance(bitrate, str) and not bitrate.endswith('k')):
                return False, "Audio bitrate must be an integer (in kbps) or string ending with 'k'"

        return True, ""

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

    def compress_video(self, input_path: str, quality_settings: Dict[str, Union[int, str, float]] = None) -> bool:
        """
        Compress the video file using FFmpeg with custom quality settings.
        
        Args:
            input_path: Path to the input video file
            quality_settings: Dictionary containing compression settings:
                - crf: Constant Rate Factor (0-51, lower is better quality)
                - preset: Compression preset (e.g., 'medium', 'fast')
                - audio_bitrate: Audio bitrate in kbps (e.g., '128k')
            
        Returns:
            bool: True if compression was successful, False otherwise
        """
        if not self.validate_input_file(input_path):
            return False

        # Set default quality settings if none provided
        if quality_settings is None:
            quality_settings = {
                'crf': 23,
                'preset': 'medium',
                'audio_bitrate': '128k'
            }

        # Validate quality settings
        is_valid, error_message = self.validate_quality_settings(quality_settings)
        if not is_valid:
            print(f"Error in quality settings: {error_message}")
            return False

        output_path = self.get_output_path(input_path)
        duration = self.get_video_duration(input_path)

        # FFmpeg compression command with custom quality settings
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'h264',
            '-crf', str(quality_settings.get('crf', 23)),
            '-preset', quality_settings.get('preset', 'medium'),
            '-c:a', 'aac',
            '-b:a', str(quality_settings.get('audio_bitrate', '128k')),
            '-y',
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
                print("\nCompression settings used:")
                print(f"CRF: {quality_settings.get('crf', 23)}")
                print(f"Preset: {quality_settings.get('preset', 'medium')}")
                print(f"Audio bitrate: {quality_settings.get('audio_bitrate', '128k')}")
                return True
            else:
                print("\n❌ Error during compression:")
                print(process.stderr.read())
                return False

        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compress MOV video files with custom quality settings.')
    parser.add_argument('input_video', help='Input video file (MOV format)')
    parser.add_argument('--crf', type=int, default=23, help='Constant Rate Factor (0-51, lower is better quality)')
    parser.add_argument('--preset', default='medium', choices=VideoCompressor.VALID_PRESETS,
                      help='Compression preset (affects compression speed and efficiency)')
    parser.add_argument('--audio-bitrate', default='128k', help='Audio bitrate (e.g., 128k, 192k, 256k)')

    args = parser.parse_args()

    quality_settings = {
        'crf': args.crf,
        'preset': args.preset,
        'audio_bitrate': args.audio_bitrate
    }

    compressor = VideoCompressor()
    success = compressor.compress_video(args.input_video, quality_settings)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
