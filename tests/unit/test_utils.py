"""
Test utility functions for the Turtle Species Identification App
"""

import pytest
import os
import tempfile
from PIL import Image
from io import BytesIO

# Import utility functions
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
from utils.file_utils import allowed_file, get_secure_filename, validate_file_size
from utils.image_utils import encode_image_to_base64, validate_image


class TestFileValidation:
    """Test file validation utilities"""
    
    def test_allowed_file_valid_extensions(self):
        """Test that valid file extensions are allowed"""
        valid_files = [
            'test.png',
            'test.jpg',
            'test.jpeg',
            'test.gif',
            'test.bmp',
            'test.webp',
            'TEST.PNG',  # Case insensitive
            'test.JPG',
            'file.name.png'  # Multiple dots
        ]
        
        for filename in valid_files:
            assert allowed_file(filename), f"Should allow {filename}"
    
    def test_allowed_file_invalid_extensions(self):
        """Test that invalid file extensions are rejected"""
        invalid_files = [
            'test.txt',
            'test.pdf',
            'test.doc',
            'test.mp4',
            'test.avi',
            'test',  # No extension
            'test.',  # Empty extension
        ]
        
        for filename in invalid_files:
            assert not allowed_file(filename), f"Should reject {filename}"
    
    def test_get_secure_filename(self):
        """Test secure filename generation"""
        # Test normal filename
        assert get_secure_filename('test.png') == 'test.png'
        
        # Test filename with path traversal
        assert get_secure_filename('../../../etc/passwd') == 'etc_passwd'
        
        # Test filename with special characters
        assert get_secure_filename('test file (1).png') == 'test_file_1.png'
    
    def test_validate_file_size(self):
        """Test file size validation"""
        # Test valid size
        assert validate_file_size(1024 * 1024)  # 1MB
        
        # Test size at limit
        assert validate_file_size(16 * 1024 * 1024)  # 16MB
        
        # Test size over limit
        assert not validate_file_size(17 * 1024 * 1024)  # 17MB
        
        # Test custom limit
        assert validate_file_size(1024, max_size=2048)  # 1KB with 2KB limit
        assert not validate_file_size(2049, max_size=2048)  # Over custom limit


class TestImageEncoding:
    """Test image encoding utilities"""
    
    def test_encode_image_to_base64(self):
        """Test that images are properly encoded to base64"""
        # Create a test image
        img = Image.new('RGB', (10, 10), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img.save(tmp_file.name, 'PNG')
            
            try:
                # Encode the image
                encoded = encode_image_to_base64(tmp_file.name)
                
                # Check that it's a valid base64 string
                assert isinstance(encoded, str)
                assert len(encoded) > 0
                
                # Try to decode it back to verify it's valid base64
                import base64
                decoded = base64.b64decode(encoded)
                assert len(decoded) > 0
                
            finally:
                # Clean up
                os.unlink(tmp_file.name)
    
    def test_encode_nonexistent_file(self):
        """Test that encoding a nonexistent file raises an exception"""
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64('nonexistent_file.png')


class TestImageProcessing:
    """Test image processing functionality"""
    
    def test_validate_image_valid(self):
        """Test that valid images pass validation"""
        img = Image.new('RGB', (100, 100), color='blue')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img.save(tmp_file.name, 'PNG')
            
            try:
                # Validate the image
                assert validate_image(tmp_file.name)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_validate_image_invalid(self):
        """Test that invalid images fail validation"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            # Write invalid image data
            tmp_file.write(b'not a valid image')
            tmp_file.flush()
            
            try:
                # This should return False
                assert not validate_image(tmp_file.name)
                
            finally:
                os.unlink(tmp_file.name)


if __name__ == '__main__':
    pytest.main([__file__])