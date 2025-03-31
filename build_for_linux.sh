#!/bin/bash

echo "======================================================"
echo "Building Minesweeper for Linux by Muhammad Saeed"
echo "======================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH!"
    echo "Please install Python 3 and try again."
    echo
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "On Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "On Arch Linux: sudo pacman -S python python-pip"
    echo
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Determine pip command (could be pip, pip3, python -m pip, etc.)
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    PIP_CMD="python3 -m pip"
fi

echo "Using pip command: $PIP_CMD"

# Install required packages
echo "Installing required packages..."
echo "Note: If this fails, try running the script with sudo."
$PIP_CMD install --user pillow pyinstaller
echo

# Check if PyInstaller is available
if ! command -v pyinstaller &> /dev/null && ! python3 -m PyInstaller --help &> /dev/null; then
    echo "WARNING: PyInstaller is not in PATH"
    echo "Attempting to use PyInstaller module directly..."
    PYINSTALLER_CMD="python3 -m PyInstaller"
else
    PYINSTALLER_CMD="pyinstaller"
fi

echo "Using PyInstaller command: $PYINSTALLER_CMD"
echo

# Create the Linux executable
echo "Building Linux executable..."
$PYINSTALLER_CMD --onefile --windowed --icon=images/unclicked_mine_tile.png --add-data "images/*:images/" --name "minesweeper" minesweeper.py

# Check if the build was successful
if [ ! -f "dist/minesweeper" ]; then
    echo "ERROR: Failed to build the executable!"
    echo "Please check the output above for errors."
    echo
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Create linux-app directory if it doesn't exist
if [ ! -d "linux-app" ]; then
    echo "Creating linux-app directory..."
    mkdir -p linux-app
fi

# Create images directory inside linux-app if it doesn't exist
if [ ! -d "linux-app/images" ]; then
    echo "Creating linux-app/images directory..."
    mkdir -p linux-app/images
fi

# Copy the executable to linux-app directory
echo "Copying executable to linux-app directory..."
cp -f dist/minesweeper linux-app/
echo

# Copy the images to linux-app/images
echo "Copying images to linux-app/images..."
cp -f images/*.png linux-app/images/
echo

# Make the executable file executable
echo "Setting executable permissions..."
chmod +x linux-app/minesweeper
echo

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -rf build
rm -rf dist
rm -f minesweeper.spec
echo

echo "======================================================"
echo "Build completed successfully!"
echo
echo "The executable is in the linux-app directory."
echo
echo "To run the game on Linux, navigate to the linux-app directory and run:"
echo "./minesweeper"
echo
echo "If you encounter a 'permission denied' error, run:"
echo "chmod +x linux-app/minesweeper"
echo "======================================================"
echo
echo "Press Enter to exit..."
read 