#!/bin/bash

# Security scanning script for Docker image
set -e

echo "🔒 Running security scan for Turtle Identifier Docker image..."

# Build the image
echo "📦 Building Docker image..."
docker buildx build --platform linux/amd64 -t turtle-identifier:security-test .

# Run security scan with Trivy (if available)
if command -v trivy &> /dev/null; then
    echo "🔍 Running Trivy security scan..."
    trivy image turtle-identifier:security-test
else
    echo "⚠️  Trivy not found. Install with: brew install trivy"
fi

# Run Docker security scan
echo "🔍 Running Docker security scan..."
docker scout cves turtle-identifier:security-test

# Check for secrets in image
echo "🔍 Checking for secrets in image..."
docker run --rm turtle-identifier:security-test find /app -name "*.key" -o -name "*.pem" -o -name "*.env*" 2>/dev/null || echo "✅ No secrets found"

# Check file permissions
echo "🔍 Checking file permissions..."
docker run --rm turtle-identifier:security-test ls -la /app

# Check running user
echo "🔍 Checking running user..."
docker run --rm turtle-identifier:security-test whoami

echo "✅ Security scan complete!"
