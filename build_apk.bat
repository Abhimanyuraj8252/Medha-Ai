@echo off
REM Medha AI - APK Build Script for Windows
REM This script builds the Android APK using Flet

REM Change to script directory
cd /d "%~dp0"

echo ============================================
echo    Medha AI - APK Build Script
echo ============================================
echo.
echo Current directory: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo [1/5] Checking Flet installation...
python -m pip show flet >nul 2>&1
if %errorlevel% neq 0 (
    echo Flet not found. Installing Flet...
    python -m pip install flet --user
)

echo.
echo [2/5] Installing required dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt --user
) else (
    echo [WARNING] requirements.txt not found in current directory
    echo Installing core dependencies...
    python -m pip install flet groq google-generativeai pyttsx3 SpeechRecognition requests beautifulsoup4 duckduckgo-search --user
)

echo.
echo [3/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [4/5] Building APK with Flet...
echo This may take 10-20 minutes on first build...
echo.

REM Add Python Scripts to PATH for flet command
set PATH=%APPDATA%\Python\Python314\Scripts;%PATH%
set PATH=%USERPROFILE%\AppData\Roaming\Python\Python314\Scripts;%PATH%
set PATH=C:\Users\%USERNAME%\AppData\Roaming\Python\Python314\Scripts;%PATH%

REM Use main_mobile.py as entry point
if exist main_mobile.py (
    echo Using main_mobile.py as entry point...
    flet build apk main_mobile.py --project "Medha AI" --org "com.medhaai" --build-number 1 --build-version "2.0.0"
) else if exist main.py (
    echo Using main.py as entry point...
    flet build apk main.py --project "Medha AI" --org "com.medhaai" --build-number 1 --build-version "2.0.0"
) else if exist src\main.py (
    echo Using src\main.py as entry point...
    flet build apk src\main.py --project "Medha AI" --org "com.medhaai" --build-number 1 --build-version "2.0.0"
) else (
    echo [ERROR] No main.py file found!
    echo Please ensure main.py or main_mobile.py exists in the project directory
    pause
    exit /b 1
)

echo.
if %errorlevel% equ 0 (
    echo ============================================
    echo [SUCCESS] APK built successfully!
    echo ============================================
    echo.
    echo APK location: build\apk\
    echo You can now install this APK on your Android phone
    echo.
    echo To install:
    echo 1. Transfer the APK to your phone
    echo 2. Enable "Install from Unknown Sources" in Settings
    echo 3. Tap the APK file to install
    echo.
) else (
    echo ============================================
    echo [ERROR] Build failed!
    echo ============================================
    echo.
    echo Common issues:
    echo - Java JDK not installed (needs JDK 11 or higher)
    echo - Android SDK not configured
    echo - Missing dependencies
    echo.
    echo For detailed guide, see APK_BUILD_GUIDE.md
    echo.
)

echo [5/5] Build process completed.
pause
