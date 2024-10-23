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

    def validate_input_file(self, input_path: str) -> bool:
        """Validate the input video file exists and has .mov extension."""
        if not os.path.exists(input_path):
            print(f"Error: Input file '{input_path}' does not exist.")
            return False
        if not input_path.lower().endswith('.mov'):
            print("Error: Input file must be a .mov file.")
            return False
        return True

    def get_output_path(self, input_path: str) -> str:
        """Generate output path by adding '_compressed' suffix."""
        base, ext = os.path.splitext(input_path)
        return f"{base}_compressed{ext}"

    def get_video_duration(self, input_path: str) -> float:
        """Get video duration in seconds using FFprobe."""
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', input_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            return 0.0

    def validate_quality_settings(self, settings: Dict[str, Union[int, str]]) -> Tuple[bool, str]:
        """Validate compression quality settings."""
        if not isinstance(settings.get('crf'), int) or settings.get('crf') < 0 or settings.get('crf') > 51:
            return False, "CRF must be between 0 and 51"
        
        if settings.get('preset') not in self.VALID_PRESETS:
            return False, f"Preset must be one of: {', '.join(self.VALID_PRESETS)}"
        
        if not isinstance(settings.get('audio_bitrate'), str) or not str(settings.get('audio_bitrate')).endswith('k'):
            return False, "Audio bitrate must be a string ending with 'k' (e.g., '128k')"
            
        return True, ""

    def compress_video(self, input_path: str, high_compression: bool = False, two_pass: bool = False) -> Optional[str]:
        """
        Compress the video with optional high compression settings.
        
        Args:
            input_path: Path to input video file
            high_compression: Enable high compression settings
            two_pass: Enable two-pass encoding for better compression
        
        Returns:
            Optional[str]: Path to compressed video file if successful, None otherwise
        """
        if not self.validate_input_file(input_path):
            return None

        output_path = self.get_output_path(input_path)
        duration = self.get_video_duration(input_path)

        # High compression settings
        settings = {
            'crf': 35 if high_compression else 23,  # Higher CRF for more compression
            'preset': 'veryslow' if high_compression else 'medium',  # Slower preset for better compression
            'audio_bitrate': '64k' if high_compression else '128k',  # Lower audio bitrate
            'scale': '1280:720' if high_compression else None,  # Scale down resolution if high compression
            'maxrate': '1M' if high_compression else None,  # Limit maximum bitrate
            'bufsize': '2M' if high_compression else None,  # Buffer size for rate control
        }

        valid, error_msg = self.validate_quality_settings(settings)
        if not valid:
            print(f"Error in quality settings: {error_msg}")
            return None

        try:
            if two_pass and high_compression:
                # First pass
                first_pass_cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c:v', 'libx264', '-preset', settings['preset'],
                    '-b:v', '0', '-crf', str(settings['crf']),
                    '-pass', '1', '-f', 'null',
                    '-an'  # No audio in first pass
                ]
                
                if settings['scale']:
                    first_pass_cmd.extend(['-vf', f'scale={settings["scale"]}'])
                
                first_pass_cmd.append('/dev/null')
                
                with tqdm(total=100, desc="First pass") as pbar:
                    process = subprocess.Popen(
                        first_pass_cmd,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    while True:
                        line = process.stderr.readline()
                        if not line:
                            break
                        if "frame=" in line and duration > 0:
                            try:
                                current_frame = int(line.split("frame=")[1].split()[0])
                                progress = min(100, int(100.0 * current_frame / (duration * 30)))
                                pbar.n = progress
                                pbar.refresh()
                            except:
                                pass
                    
                    process.wait()
                    if process.returncode != 0:
                        raise Exception("First pass encoding failed")
                
                # Second pass
                second_pass_cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c:v', 'libx264', '-preset', settings['preset'],
                    '-b:v', '0', '-crf', str(settings['crf']),
                    '-pass', '2',
                    '-c:a', 'aac', '-b:a', settings['audio_bitrate']
                ]
                
                if settings['scale']:
                    second_pass_cmd.extend(['-vf', f'scale={settings["scale"]}'])
                if settings['maxrate']:
                    second_pass_cmd.extend(['-maxrate', settings['maxrate'], '-bufsize', settings['bufsize']])
                
                second_pass_cmd.append(output_path)
                
                with tqdm(total=100, desc="Second pass") as pbar:
                    process = subprocess.Popen(
                        second_pass_cmd,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    while True:
                        line = process.stderr.readline()
                        if not line:
                            break
                        if "frame=" in line and duration > 0:
                            try:
                                current_frame = int(line.split("frame=")[1].split()[0])
                                progress = min(100, int(100.0 * current_frame / (duration * 30)))
                                pbar.n = progress
                                pbar.refresh()
                            except:
                                pass
                    
                    process.wait()
                    if process.returncode != 0:
                        raise Exception("Second pass encoding failed")
                
            else:
                # Single pass encoding
                cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c:v', 'libx264', '-preset', settings['preset'],
                    '-crf', str(settings['crf']),
                    '-c:a', 'aac', '-b:a', settings['audio_bitrate']
                ]
                
                if settings['scale']:
                    cmd.extend(['-vf', f'scale={settings["scale"]}'])
                if settings['maxrate']:
                    cmd.extend(['-maxrate', settings['maxrate'], '-bufsize', settings['bufsize']])
                
                cmd.append(output_path)
                
                with tqdm(total=100, desc="Compressing") as pbar:
                    process = subprocess.Popen(
                        cmd,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    while True:
                        line = process.stderr.readline()
                        if not line:
                            break
                        if "frame=" in line and duration > 0:
                            try:
                                current_frame = int(line.split("frame=")[1].split()[0])
                                progress = min(100, int(100.0 * current_frame / (duration * 30)))
                                pbar.n = progress
                                pbar.refresh()
                            except:
                                pass
                    
                    process.wait()
                    if process.returncode != 0:
                        raise Exception("Compression failed")

            # Wait for file to be completely written
            time.sleep(1)
            
            # Print compression results
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            reduction = (1 - output_size/input_size) * 100
            
            print(f"\nCompression Results:")
            print(f"Original size: {input_size/1024/1024:.2f} MB")
            print(f"Compressed size: {output_size/1024/1024:.2f} MB")
            print(f"Size reduction: {reduction:.2f}%")
            
            return output_path
            
        except Exception as e:
            print(f"Error during compression: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_compressor.py <input_file> [--high-compression] [--two-pass]")
        sys.exit(1)

    input_file = sys.argv[1]
    high_compression = "--high-compression" in sys.argv
    two_pass = "--two-pass" in sys.argv
    
    compressor = VideoCompressor()
    result = compressor.compress_video(input_file, high_compression=high_compression, two_pass=two_pass)
    
    if result:
        print(f"\nCompressed video saved to: {result}")
    else:
        print("\nCompression failed!")
