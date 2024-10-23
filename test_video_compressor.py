import unittest
import os
import tempfile
from video_compressor import VideoCompressor

class TestVideoCompressor(unittest.TestCase):
    def setUp(self):
        self.compressor = VideoCompressor()
        self.temp_dir = tempfile.mkdtemp()

    def test_validate_input_file_nonexistent(self):
        """Test validation of non-existent file"""
        self.assertFalse(self.compressor.validate_input_file("nonexistent.mov"))

    def test_validate_input_file_wrong_extension(self):
        """Test validation of file with wrong extension"""
        with tempfile.NamedTemporaryFile(suffix='.mp4') as tmp_file:
            self.assertFalse(self.compressor.validate_input_file(tmp_file.name))

    def test_get_output_path(self):
        """Test output path generation"""
        input_path = "/path/to/video.mov"
        expected = "/path/to/video_compressed.mov"
        self.assertEqual(self.compressor.get_output_path(input_path), expected)

    def tearDown(self):
        # Clean up temporary directory
        os.rmdir(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
