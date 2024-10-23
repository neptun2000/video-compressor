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

    def test_validate_quality_settings_valid(self):
        """Test validation of valid quality settings"""
        settings = {
            'crf': 23,
            'preset': 'medium',
            'audio_bitrate': '128k'
        }
        is_valid, _ = self.compressor.validate_quality_settings(settings)
        self.assertTrue(is_valid)

    def test_validate_quality_settings_invalid_crf(self):
        """Test validation of invalid CRF value"""
        settings = {
            'crf': 52,  # Invalid: should be 0-51
            'preset': 'medium',
            'audio_bitrate': '128k'
        }
        is_valid, error_msg = self.compressor.validate_quality_settings(settings)
        self.assertFalse(is_valid)
        self.assertIn("CRF must be between 0 and 51", error_msg)

    def test_validate_quality_settings_invalid_preset(self):
        """Test validation of invalid preset"""
        settings = {
            'crf': 23,
            'preset': 'invalid_preset',  # Invalid preset
            'audio_bitrate': '128k'
        }
        is_valid, error_msg = self.compressor.validate_quality_settings(settings)
        self.assertFalse(is_valid)
        self.assertIn("Preset must be one of:", error_msg)

    def test_validate_quality_settings_invalid_audio_bitrate(self):
        """Test validation of invalid audio bitrate"""
        settings = {
            'crf': 23,
            'preset': 'medium',
            'audio_bitrate': 128  # Invalid format: should be string with 'k'
        }
        is_valid, error_msg = self.compressor.validate_quality_settings(settings)
        self.assertFalse(is_valid)
        self.assertIn("Audio bitrate must be", error_msg)

    def tearDown(self):
        # Clean up temporary directory
        os.rmdir(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
