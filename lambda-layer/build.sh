#!/bin/bash
# Build script for Lambda Layer dependencies

set -e

echo "🚀 Building Lambda Layer dependencies..."

# Clean previous builds
rm -rf python
mkdir -p python/lib/python3.13/site-packages

# Install dependencies
pip install -r requirements.txt -t python/lib/python3.13/site-packages --no-deps

# Remove unnecessary files
find python/lib/python3.13/site-packages -name "*.pyc" -delete
find python/lib/python3.13/site-packages -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find python/lib/python3.13/site-packages -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find python/lib/python3.13/site-packages -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Create deployment package
echo "📦 Creating deployment package..."
zip -r9 ../lambda-layer.zip python

echo "✅ Lambda Layer built successfully!"
echo "📄 Layer package: lambda-layer.zip"
echo "📊 Package size: $(du -sh lambda-layer.zip | cut -f1)"
