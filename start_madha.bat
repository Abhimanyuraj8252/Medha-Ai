@echo off
REM Change to script directory first
cd /d "%~dp0"

TITLE Medha AI - Launcher
COLOR 0A
echo ===================================================
echo        STARTING MEDHA AI (1000 Legion Power)
echo ===================================================
echo.
echo Current Directory: %CD%
echo.

REM Ensure Python Scripts is on PATH to avoid warnings
for /f "delims=" %%p in ('py -3.12 -c "import sys; print(sys.exec_prefix)"') do set "PY312_PREFIX=%%p"
if exist "%PY312_PREFIX%\Scripts" (
    set "PATH=%PY312_PREFIX%\Scripts;%PATH%"
)

REM Force software rendering to avoid black window in native app
set "FLET_FORCE_SOFTWARE_RENDERING=1"
set "FLET_WEB_RENDERER=html"
set "MEDHA_USE_BROWSER=0"

REM Check WebView2 Runtime (required for Flet native app on Windows)
reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    reg query "HKCU\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv >nul 2>&1
)
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] WebView2 Runtime not found. Native app may show black screen.
    echo Install: https://developer.microsoft.com/microsoft-edge/webview2/
    echo.
)

echo [INFO] Clearing port 8550 if already in use...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8550 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo [Step 1/4] Checking Core Dependencies...
py -3.12 -c "import flet" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing Flet...
    py -3.12 -m pip install flet --quiet --no-warn-script-location
)
py -3.12 -m pip install groq requests psutil ddgs wikipedia --quiet --no-warn-script-location
IF %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo [CRITICAL ERROR] Failed to install Core Dependencies.
    pause
    exit /b
)

echo [Step 2/4] Installing File Processing Libraries...
py -3.12 -m pip install Pillow PyPDF2 python-docx pytesseract pdf2image --quiet --no-warn-script-location
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some file types might not be fully supported.
)

echo [INFO] For OCR (image/PDF text), install external tools:
echo 1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Poppler (for PDF OCR): https://github.com/oschwartz10612/poppler-windows/releases
echo.

where tesseract >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Tesseract not found in PATH. OCR for images may not work.
)
where pdftoppm >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Poppler not found in PATH. OCR for scanned PDFs may not work.
)

echo [Step 3/4] Installing Voice Dependencies...
py -3.12 -m pip install gTTS SpeechRecognition edge-tts --quiet --no-warn-script-location
IF %ERRORLEVEL% NEQ 0 (
    REM Fallback for other python versions
    python -m pip install gTTS SpeechRecognition edge-tts --quiet --no-warn-script-location
)
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Voice Text-to-Speech might not work.
)

echo [Step 4/4] Installing Audio Engine...
py -3.12 -m pip install pygame --quiet --no-warn-script-location 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Audio engine installed successfully.
) ELSE (
    py -3.12 -m pip install playsound==1.2.2 --quiet --no-warn-script-location 2>nul
    IF %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Alternative audio engine installed.
    ) ELSE (
        echo [NOTICE] Audio playback may be limited. Using system audio.
    )
)

echo [Step 5/5] Installing Microphone Support...
echo [INFO] Voice features require PyAudio...
echo.

REM Check if PyAudio is already installed
py -3.12 -c "import pyaudio" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] PyAudio is already installed.
    goto :audio_done
)

REM Install PyAudio for Python 3.12 (prebuilt wheels available)
echo [INFO] Installing PyAudio for Python 3.12...
py -3.12 -m pip install pyaudio --quiet --no-warn-script-location
IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Microphone support enabled!
    goto :audio_done
)

echo.
echo ======================================================
echo [INFO] PyAudio Installation Skipped
echo ======================================================
echo PyAudio requires Microsoft Visual C++ Build Tools.
echo.
echo The app will work fine with TEXT INPUT and VOICE OUTPUT.
echo Only MICROPHONE INPUT will be disabled.
echo.
echo To enable microphone (optional):
echo 1. Download: https://aka.ms/vs/17/release/vs_BuildTools.exe
echo 2. Install "Desktop development with C++" workload
echo 3. Run: pip install pyaudio
echo.
echo Press any key to continue with text-only input...
======================================================
pause >nul

:audio_done

echo.
echo Launching Application...
echo.

REM Check which main.py file exists
if exist "src\main.py" (
    echo [INFO] Using src\main.py
    py -3.12 src\main.py
    IF %ERRORLEVEL% NEQ 0 (
        python src\main.py
    )
) else if exist "main.py" (
    echo [INFO] Using main.py in current directory
    py -3.12 main.py
    IF %ERRORLEVEL% NEQ 0 (
        python main.py
    )
) else (
    COLOR 0C
    echo [ERROR] No main.py file found!
    echo Please ensure you are in the correct directory.
)
) else (
    if exist "main_mobile.py" (
        echo [INFO] Using main_mobile.py (mobile version)
        py -3.12 main_mobile.py
        IF %ERRORLEVEL% NEQ 0 (
            python main_mobile.py
        )
    ) else (
        COLOR 0C
        echo [ERROR] No main.py file found!
        echo Please ensure you are in the correct directory.
        echo Expected files: main.py, main_mobile.py, or src\main.py
    )
)

IF %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo.
    echo [ERROR] The application crashed.
    echo Common fixes:
    echo 1. Ensure Python 3.10+ is installed.
    echo 2. Run: pip install -r requirements.txt
    echo 3. Check if all dependencies are installed.
)

echo.
echo [INFO] App session ended.
pause
