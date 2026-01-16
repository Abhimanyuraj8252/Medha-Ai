@echo off
TITLE Medha AI - Launcher
COLOR 0A
echo ===================================================
echo        STARTING MEDHA AI (1000 Legion Power)
echo ===================================================
echo.

echo [Step 1/4] Installing Core Dependencies...
py -3.12 -m pip install flet groq requests psutil ddgs wikipedia --quiet
IF %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo [CRITICAL ERROR] Failed to install Core Dependencies.
    pause
    exit /b
)

echo [Step 2/4] Installing File Processing Libraries...
py -3.12 -m pip install Pillow PyPDF2 python-docx --quiet
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some file types might not be fully supported.
)

echo [Step 3/4] Installing Voice Dependencies...
py -3.12 -m pip install gTTS SpeechRecognition edge-tts --quiet
IF %ERRORLEVEL% NEQ 0 (
    REM Fallback for other python versions
    python -m pip install gTTS SpeechRecognition edge-tts --quiet
)
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Voice Text-to-Speech might not work.
)

echo [Step 4/4] Installing Audio Engine...
py -3.12 -m pip install pygame --quiet 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Audio engine installed successfully.
) ELSE (
    py -3.12 -m pip install playsound==1.2.2 --quiet 2>nul
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
py -3.12 -m pip install pyaudio --quiet
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

cd src
py -3.12 main.py
IF %ERRORLEVEL% NEQ 0 (
    python main.py
    IF %ERRORLEVEL% NEQ 0 (
        COLOR 0C
        echo.
        echo [ERROR] The application crashed.
        echo Common fixes:
        echo 1. Ensure Python 3.10+ is installed.
        echo 2. Run pip install flet manually to check for errors.
    )
)
cd ..

echo.
echo [INFO] App session ended.
pause
