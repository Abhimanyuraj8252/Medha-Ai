#!/bin/bash
# Medha AI - APK Build Script for Linux/Mac
# This script builds the Android APK using Flet

echo "============================================"
echo "   Medha AI - APK Build Script"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "[1/5] Checking Flet installation..."
if ! pip3 show flet &> /dev/null; then
    echo "Flet not found. Installing Flet..."
    pip3 install flet
fi

echo ""
echo "[2/5] Installing required dependencies..."
pip3 install -r requirements.txt

echo ""
echo "[3/5] Cleaning previous builds..."
rm -rf build dist

echo ""
echo "[4/5] Building APK with Flet..."
echo "This may take 10-20 minutes on first build..."
echo ""

# Build APK using Flet's build command
flet build apk --project "Medha AI" --org "com.medhaai" --build-number 1 --build-version "2.0.0"

echo ""
if [ $? -eq 0 ]; then
    echo "============================================"
    echo "[SUCCESS] APK built successfully!"
    echo "============================================"
    echo ""
    echo "APK location: build/apk/"
    echo "You can now install this APK on your Android phone"
    echo ""
    echo "To install:"
    echo "1. Transfer the APK to your phone"
    echo "2. Enable 'Install from Unknown Sources' in Settings"
    echo "3. Tap the APK file to install"
    echo ""
else
    echo "============================================"
    echo "[ERROR] Build failed!"
    echo "============================================"
    echo ""
    echo "Common issues:"
    echo "- Java JDK not installed (needs JDK 11 or higher)"
    echo "- Android SDK not configured"
    echo "- Missing dependencies"
    echo ""
    echo "For detailed guide, see APK_BUILD_GUIDE.md"
    echo ""
fi

echo "[5/5] Build process completed."
