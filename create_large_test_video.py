import numpy as np
import cv2
import os

def create_large_test_video(filename="large_test_video.mov", duration=300, fps=60, resolution=(3840, 2160)):
    """
    Create a large 4K test video file
    Args:
        filename: output filename
        duration: video duration in seconds (5 minutes)
        fps: frames per second (60 fps for high quality)
        resolution: video resolution (4K: 3840x2160)
    """
    width, height = resolution
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    # Create frames with moving patterns and gradients
    for i in range(duration * fps):
        # Create a colorful moving pattern
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create dynamic gradients
        t = i / (duration * fps)
        for y in range(height):
            for x in range(width):
                b = int(128 + 127 * np.sin(x * 0.01 + t * 5))
                g = int(128 + 127 * np.sin(y * 0.01 + t * 3))
                r = int(128 + 127 * np.sin((x + y) * 0.01 + t * 4))
                frame[y, x] = [b, g, r]
        
        # Add moving text
        text = f"4K Test Video - Frame {i}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 2, 3)[0]
        x = int((width - text_size[0]) / 2)
        y = int(height/2 + 100 * np.sin(t * 2))
        cv2.putText(frame, text, (x, y), font, 2, (255, 255, 255), 3)
        
        out.write(frame)
        
        # Print progress
        if i % fps == 0:
            print(f"Progress: {i/(duration * fps)*100:.1f}%")
    
    out.release()
    print(f"\nCreated large test video: {filename}")
    print(f"File size: {os.path.getsize(filename) / (1024*1024*1024):.2f} GB")

if __name__ == "__main__":
    create_large_test_video()
