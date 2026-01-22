#!/bin/bash

echo "🚀 Setting up RFP Frontend for cross-platform development..."

# Detect platform
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo "Platform: $PLATFORM $ARCH"

# Clean node_modules and package-lock.json to ensure fresh install
echo "🧹 Cleaning existing dependencies..."
rm -rf node_modules package-lock.json

# Install dependencies based on platform
if [[ "$PLATFORM" == "Darwin" ]]; then
    echo "🍎 Detected macOS"
    if [[ "$ARCH" == "arm64" ]]; then
        echo "📱 Apple Silicon detected"
        npm install
    else
        echo "💻 Intel Mac detected"
        npm install
    fi
elif [[ "$PLATFORM" == "Linux" ]]; then
    echo "🐧 Detected Linux"
    npm install
elif [[ "$PLATFORM" == "MINGW"* ]] || [[ "$PLATFORM" == "CYGWIN"* ]] || [[ "$PLATFORM" == "MSYS"* ]]; then
    echo "🪟 Detected Windows (Git Bash)"
    npm install
else
    echo "❓ Unknown platform, attempting standard install..."
    npm install
fi

# Verify installation
echo "✅ Verifying installation..."
if npm list next > /dev/null 2>&1; then
    echo "✅ Next.js installed successfully"
else
    echo "❌ Next.js installation failed"
    exit 1
fi

if npm list tailwindcss > /dev/null 2>&1; then
    echo "✅ Tailwind CSS installed successfully"
else
    echo "❌ Tailwind CSS installation failed"
    exit 1
fi

echo "🎉 Setup complete! You can now run:"
echo "   npm run dev    # Start development server"
echo "   npm run build  # Build for production"
echo "   npm run start  # Start production server"
