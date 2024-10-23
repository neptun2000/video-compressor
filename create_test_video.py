import numpy as np
import cv2
import os

def create_test_video(filename="test_video.mov", duration=5, fps=30):
    # Set video properties
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    # Create frames with moving text
    for i in range(duration * fps):
        # Create a black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Add some moving text
        text = "Test Video"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        x = int((width - text_size[0]) / 2)
        y = int(height/2 + i % 50)  # Moving text up and down
        cv2.putText(frame, text, (x, y), font, 1, (255, 255, 255), 2)
        out.write(frame)
    
    out.release()
    print(f"Created test video: {filename}")

if __name__ == "__main__":
    create_test_video()
