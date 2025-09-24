# Production stage with security-focused approach
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID/GID for security
RUN groupadd -r appuser && useradd -r -g appuser -u 1001 appuser

# Set working directory
WORKDIR /app

# Copy production requirements first for better caching
COPY requirements-prod.txt requirements.txt

# Install Python dependencies as root (needed for system packages)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Create uploads directory with proper permissions
RUN mkdir -p uploads && chown -R appuser:appuser uploads

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check with proper user context
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run the application
CMD ["python", "app.py"]
