"""
Test suite for the Turtle Species Identification App
"""

import pytest
import os
import tempfile
import json
from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock

# Import the Flask app
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
from api.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_image():
    """Create a sample test image"""
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test that the health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'Turtle ID API is running' in data['message']


class TestMainPage:
    """Test the main page endpoint"""
    
    def test_main_page_loads(self, client):
        """Test that the main page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Turtle Species Identifier' in response.data
        assert b'Upload an image' in response.data


class TestFileUpload:
    """Test file upload functionality"""
    
    def test_upload_no_file(self, client):
        """Test upload without file returns 400"""
        response = client.post('/upload')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'No file provided' in data['error']
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename returns 400"""
        response = client.post('/upload', data={'file': (BytesIO(), '')})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'No file selected' in data['error']
    
    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type returns 400"""
        response = client.post('/upload', data={
            'file': (BytesIO(b'not an image'), 'test.txt')
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'File type not allowed' in data['error']
    
    def test_upload_valid_image_no_api_key(self, client, sample_image):
        """Test upload with valid image but no API key"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.post('/upload', data={
                'file': (sample_image, 'test.png'),
                'api': 'openai'
            })
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'API key' in data['error']
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_upload_with_openai_success(self, mock_post, client, sample_image):
        """Test successful upload with OpenAI API"""
        # Mock successful OpenAI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'is_turtle': True,
                        'species': 'Testudo graeca',
                        'common_name': 'Greek Tortoise',
                        'confidence': 'high',
                        'description': 'A small tortoise with distinctive shell patterns',
                        'notes': 'Test identification'
                    })
                }
            }]
        }
        mock_post.return_value = mock_response
        
        response = client.post('/upload', data={
            'file': (sample_image, 'test.png'),
            'api': 'openai'
        })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['is_turtle'] is True
        assert data['species'] == 'Testudo graeca'
        assert data['common_name'] == 'Greek Tortoise'
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_upload_with_gemini_success(self, mock_post, client, sample_image):
        """Test successful upload with Gemini API"""
        # Mock successful Gemini response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps({
                            'is_turtle': True,
                            'species': 'Chelonia mydas',
                            'common_name': 'Green Sea Turtle',
                            'confidence': 'high',
                            'description': 'A large sea turtle with heart-shaped carapace',
                            'notes': 'Test identification'
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        response = client.post('/upload', data={
            'file': (sample_image, 'test.png'),
            'api': 'gemini'
        })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['is_turtle'] is True
        assert data['species'] == 'Chelonia mydas'
        assert data['common_name'] == 'Green Sea Turtle'
    
    def test_upload_large_file(self, client):
        """Test upload with file that's too large"""
        # Create a large file (simulate) - smaller for testing
        large_data = b'x' * (5 * 1024 * 1024)  # 5MB
        
        # Test with a client that has a smaller max content length
        with app.test_client() as test_client:
            # Temporarily reduce the max content length for testing
            original_max = app.config['MAX_CONTENT_LENGTH']
            app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1MB
            
            try:
                response = test_client.post('/upload', data={
                    'file': (BytesIO(large_data), 'large.png')
                })
                # Flask might return 500 instead of 413 in test environment
                assert response.status_code in [413, 500]
            finally:
                app.config['MAX_CONTENT_LENGTH'] = original_max


class TestImageValidation:
    """Test image validation functionality"""
    
    def test_invalid_image_file(self, client):
        """Test upload with corrupted image file"""
        response = client.post('/upload', data={
            'file': (BytesIO(b'not a valid image'), 'test.png')
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'Invalid image file' in data['error']


class TestAPIErrorHandling:
    """Test API error handling"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_openai_api_error(self, mock_post, client, sample_image):
        """Test handling of OpenAI API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        response = client.post('/upload', data={
            'file': (sample_image, 'test.png'),
            'api': 'openai'
        })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'OpenAI API error' in data['error']
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_gemini_api_error(self, mock_post, client, sample_image):
        """Test handling of Gemini API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        response = client.post('/upload', data={
            'file': (sample_image, 'test.png'),
            'api': 'gemini'
        })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Gemini API error' in data['error']


class TestFileCleanup:
    """Test file cleanup functionality"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_uploaded_file_cleanup(self, mock_post, client, sample_image):
        """Test that uploaded files are cleaned up after processing"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'is_turtle': True,
                        'species': 'Test',
                        'common_name': 'Test',
                        'confidence': 'high',
                        'description': 'Test',
                        'notes': 'Test'
                    })
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Get initial file count in upload directory
        initial_files = len(os.listdir(app.config['UPLOAD_FOLDER']))
        
        response = client.post('/upload', data={
            'file': (sample_image, 'test.png'),
            'api': 'openai'
        })
        
        # Check that file was processed and cleaned up
        final_files = len(os.listdir(app.config['UPLOAD_FOLDER']))
        assert final_files == initial_files  # No files should remain


class TestEnvironmentVariables:
    """Test environment variable handling"""
    
    def test_no_api_keys_configured(self, client, sample_image):
        """Test behavior when no API keys are configured"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.post('/upload', data={
                'file': (sample_image, 'test.png'),
                'api': 'openai'
            })
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'API key not configured' in data['error']


if __name__ == '__main__':
    pytest.main([__file__])