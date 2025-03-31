@echo off
echo ======================================================
echo Building Minesweeper for Windows by Muhammad Saeed
echo ======================================================
echo.

:: Install PyInstaller if not installed
echo Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)
echo.

:: Create the Windows executable
echo Building Windows executable...
pyinstaller --onefile --windowed --icon=images/unclicked_mine_tile.png --add-data "images/*;images/" --name "Minesweeper_By_Muhammad" minesweeper.py
echo.

:: Create windows-app directory if it doesn't exist
if not exist windows-app (
    echo Creating windows-app directory...
    mkdir windows-app
)

:: Create images directory inside windows-app if it doesn't exist
if not exist windows-app\images (
    echo Creating windows-app\images directory...
    mkdir windows-app\images
)

:: Copy the executable to windows-app directory
echo Copying executable to windows-app directory...
copy /Y dist\Minesweeper_By_Muhammad.exe windows-app\Minesweeper.exe
echo.

:: Copy the images to windows-app\images
echo Copying images to windows-app\images...
copy /Y images\*.png windows-app\images\
echo.

:: Clean up temporary files
echo Cleaning up temporary files...
rmdir /S /Q build
rmdir /S /Q dist
del /Q Minesweeper_By_Muhammad.spec
echo.

echo ======================================================
echo Build completed successfully!
echo.
echo The executable is in the windows-app directory.
echo.
echo Note: Windows Defender might scan the executable 
echo as it's created with PyInstaller. This is normal
echo and you can safely ignore the warning.
echo ======================================================
echo.
echo Press any key to exit...
pause > nul 