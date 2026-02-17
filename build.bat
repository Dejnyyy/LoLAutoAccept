@echo off
echo ========================================
echo   Building LoL Auto-Accept .exe
echo ========================================
echo.

REM Install PyInstaller if not present
pip install pyinstaller 2>nul

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "LoLAutoAccept.spec" del /q LoLAutoAccept.spec

REM Build single-file executable
python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name "LoLAutoAccept" ^
    --icon=icon.ico ^
    --hidden-import=pystray._win32 ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageDraw ^
    main.py

echo.
if exist "dist\LoLAutoAccept.exe" (
    echo ========================================
    echo   Build complete!
    echo   Output: dist\LoLAutoAccept.exe
    echo ========================================
) else (
    echo ========================================
    echo   BUILD FAILED - check output above
    echo ========================================
)
pause
