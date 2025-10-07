@echo off
echo ================================
echo    LostKit - Windows Setup
echo ================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Found Python version: %PYTHON_VERSION%

echo.
echo Checking for required packages...
echo.

REM Check if packages are installed using pip show (more reliable)
python -m pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo PyQt6 is not installed.
    set /p install_pyqt6="Do you want to install PyQt6? (Y/N): "
    if /i "!install_pyqt6!"=="Y" (
        echo Installing PyQt6...
        python -m pip install PyQt6
        if errorlevel 1 (
            echo ERROR: Failed to install PyQt6!
            pause
            exit /b 1
        )
    ) else (
        echo PyQt6 installation skipped.
    )
) else (
    echo PyQt6 already installed
)

python -m pip show PyQt6-WebEngine >nul 2>&1
if errorlevel 1 (
    echo PyQt6-WebEngine is not installed.
    set /p install_webengine="Do you want to install PyQt6-WebEngine? (Y/N): "
    if /i "!install_webengine!"=="Y" (
        echo Installing PyQt6-WebEngine...
        python -m pip install PyQt6-WebEngine
        if errorlevel 1 (
            echo ERROR: Failed to install PyQt6-WebEngine!
            pause
            exit /b 1
        )
    ) else (
        echo PyQt6-WebEngine installation skipped.
    )
) else (
    echo PyQt6-WebEngine already installed
)

echo.
echo ================================
echo    Starting LostKit...
echo ================================
echo.
timeout /t 1 /nobreak >nul

REM Hide the console window when launching the app
start "" /B python main.py
exit