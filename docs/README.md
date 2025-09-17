# Turtle Species Identification App

A professional, well-organized web application that uses AI vision APIs to identify turtle species from uploaded images. This proof-of-concept demonstrates the integration of existing AI models for species identification without requiring custom model training.

## 🏗️ Project Structure

The project is organized into logical, maintainable directories:

```
Proof-Of-Concept-Demo/
├── main.py                     # 🚀 Main entry point
├── Dockerfile                  # 🐳 Container configuration
├── .github/                    # ⚙️ GitHub workflows & templates
├── config/                     # ⚙️ Configuration files
├── docs/                       # 📚 Documentation
├── scripts/                    # 🔧 Utility scripts
├── src/                        # 💻 Source code
│   ├── api/                   # 🌐 API layer
│   ├── utils/                 # 🛠️ Utility modules
│   └── templates/             # 🎨 HTML templates
├── tests/                      # 🧪 Test suite
│   └── unit/                  # 🔬 Unit tests
└── uploads/                    # 📁 Temporary storage
```

## ✨ Features

- 🐢 **Turtle Species Identification** using AI vision APIs
- 🤖 **Multiple AI Services** - OpenAI GPT-4 Vision & Google Gemini Vision
- 📱 **Modern Web Interface** with drag-and-drop upload
- 🔒 **Secure File Processing** with validation and sanitization
- ⚡ **Real-time Processing** with loading states
- 🧪 **Comprehensive Testing** with 88% code coverage
- 🚀 **CI/CD Pipeline** with GitHub Actions
- 🐳 **Docker Support** for easy deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- API key for at least one AI service (OpenAI or Gemini)

### Installation

1. **Clone and navigate to the project**
   ```bash
   git clone <repository-url>
   cd Proof-Of-Concept-Demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp config/env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8080`

## 🧪 Testing

### Run Tests
```bash
# All tests
python scripts/run_tests.py

# Backend tests only
python scripts/run_tests.py --type backend

# With coverage
python scripts/run_tests.py --coverage

# Using Make
make test
make test-backend
```

### Test Coverage
- **22 comprehensive tests**
- **88% code coverage**
- **Unit tests** for all components
- **Integration tests** for API workflows
- **Error handling tests** for robustness

## 📚 Documentation

- **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed directory organization
- **[Testing Guide](TESTING.md)** - Comprehensive testing documentation
- **[API Documentation](API.md)** - Endpoint specifications (coming soon)

## 🔧 Development

### Project Organization
- **Separation of Concerns** - API, utils, and templates separated
- **Modular Design** - Easy to add new features
- **Test-Driven** - Comprehensive test coverage
- **Documentation-First** - Well-documented codebase

### Adding New Features
1. Add utility functions to `src/utils/`
2. Add API endpoints to `src/api/app.py`
3. Update templates in `src/templates/`
4. Add tests to `tests/unit/`
5. Update documentation in `docs/`

### Code Quality
- **Linting** - Flake8 for code quality
- **Security** - Bandit for security scanning
- **Dependencies** - Safety for vulnerability checks
- **Formatting** - Consistent code style

## 🚀 Deployment

### Docker
```bash
# Build image
docker build -t turtle-species-id .

# Run container
docker run -p 8080:8080 --env-file .env turtle-species-id
```

### Production
- Use Gunicorn as WSGI server
- Configure reverse proxy (Nginx)
- Set up proper environment variables
- Enable HTTPS

## 🔒 Security

- **File Validation** - Type and size checking
- **Input Sanitization** - Secure filename handling
- **API Key Protection** - Environment variable management
- **Error Handling** - Secure error responses
- **CORS Protection** - Cross-origin request handling

## 🤖 AI Services

### OpenAI GPT-4 Vision (Recommended)
- High accuracy for species identification
- Detailed scientific and common names
- Structured JSON responses
- Confidence level reporting

### Google Gemini Vision
- Fast and cost-effective
- Good accuracy for species identification
- Alternative to OpenAI
- Reliable performance

## 📊 Performance

- **Fast Processing** - Optimized image handling
- **Memory Efficient** - Automatic file cleanup
- **Scalable** - Modular architecture
- **Reliable** - Comprehensive error handling

## 🛠️ Technology Stack

- **Backend** - Python 3.8+, Flask 2.3.3
- **Frontend** - HTML5, CSS3, JavaScript (ES6+)
- **AI Integration** - OpenAI API, Google Gemini API
- **Testing** - pytest, coverage
- **Containerization** - Docker
- **CI/CD** - GitHub Actions

## 📈 Future Enhancements

- **Frontend Testing** - Visual regression testing
- **Database Integration** - Result storage
- **User Authentication** - User management
- **Batch Processing** - Multiple image upload
- **API Versioning** - Backward compatibility
- **Monitoring** - Application metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ for turtle conservation and AI education**