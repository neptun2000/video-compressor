import unittest
import os
import tempfile
from video_compressor import VideoCompressor
import shutil

class TestHighCompression(unittest.TestCase):
    def setUp(self):
        self.compressor = VideoCompressor()
        self.test_video = "test_video.mov"
        
    def test_high_compression(self):
        """Test high compression settings result in smaller file size"""
        # First compress with normal settings
        normal_output = self.compressor.compress_video(self.test_video, high_compression=False)
        self.assertIsNotNone(normal_output)
        normal_size = os.path.getsize(normal_output)
        
        # Then compress with high compression
        high_output = self.compressor.compress_video(self.test_video, high_compression=True)
        self.assertIsNotNone(high_output)
        high_size = os.path.getsize(high_output)
        
        # High compression should result in smaller file
        self.assertLess(high_size, normal_size)
        
    def test_two_pass_encoding(self):
        """Test two-pass encoding with high compression"""
        # Compress with high compression and two-pass
        output = self.compressor.compress_video(self.test_video, high_compression=True, two_pass=True)
        self.assertIsNotNone(output)
        
        # Verify file exists and has non-zero size
        self.assertTrue(os.path.exists(output))
        self.assertGreater(os.path.getsize(output), 0)

if __name__ == '__main__':
    unittest.main()
