# Build Instructions

This file contains instructions for building executable files for the Minesweeper game on Windows and Linux systems.

## Requirements

- Python 3.6 or newer
- Required Python libraries:
  - tkinter (comes with most Python installations)
  - Pillow
  - pyinstaller

## Building for Windows

1. Open Command Prompt in the game folder
2. Run the following file:
   ```
   build_for_windows.bat
   ```
3. Wait until the build process completes
4. You will find the executable file `Minesweeper.exe` in the `windows-app` folder

## Building for Linux

### Prerequisites:

Before building the game on Linux, make sure to install the basic requirements:

```bash
# For Debian-based distributions (Ubuntu, Linux Mint, etc.)
sudo apt update
sudo apt install python3 python3-pip python3-tk

# For Fedora/RHEL-based distributions
sudo dnf install python3 python3-pip python3-tkinter

# For Arch Linux
sudo pacman -S python python-pip tk
```

### Build Steps:

1. Open Terminal in the game folder
2. Make the build file executable:
   ```
   chmod +x build_for_linux.sh
   ```
3. Run the build file:
   ```
   ./build_for_linux.sh
   ```
   If you encounter permission issues, try:
   ```
   sudo ./build_for_linux.sh
   ```
4. Wait until the build process completes
5. You will find the executable file `minesweeper` in the `linux-app` folder

### Running the Game on Linux:

```bash
cd linux-app
./minesweeper
```

If you get a "permission denied" error, run:
```bash
chmod +x minesweeper
```

## Important Notes

- You may see a warning from antivirus software in Windows during the build process or when running the executable file. This is normal with files created by PyInstaller and can be safely ignored.
- The resulting executable files are standalone and do not require Python or any other libraries to be installed.
- You can move the `windows-app` and `linux-app` folders anywhere, but you must maintain the folder structure (the `images` folder inside the main folder).

## Troubleshooting

### Windows Issues:

- If you see a warning from Windows Defender, you can click on "More info" and then "Run anyway".
- If images don't appear in the game, make sure the `images` folder is in the same folder as the executable file.

### Linux Issues:

- **Missing tkinter**: Install the tkinter package appropriate for your distribution.
- **"Cannot connect to X server" error**: Make sure you're running the game in a graphical environment (GUI).
- **Cannot find pip or pyinstaller**: The script will try to detect the correct command, but you can install them manually:
  ```
  python3 -m pip install --user pip
  python3 -m pip install --user pyinstaller pillow
  ```

## Developer

Muhammad Saeed | https://github.com/mid0o 