"""
Build Script for APNA Computer RMS
Generates a standalone Windows Executable (.exe) using PyInstaller
Usage:
    python -m pip install pyinstaller
    python build_installer.py
"""
import os
import subprocess
import sys

def build():
    print("🚀 Starting build process for APNA Computer RMS...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=APNA_Computer_RMS",
        "--onefile",
        "--windowed", # No black command prompt console
        "--noconsole",
        "--collect-all=customtkinter",
        "--version-file=file_version_info.txt",
        "--add-data=Logo.png;.",
        "--add-data=app_config.json;.",
        "--add-data=fonts;fonts",
        "--add-data=core;core",
        "--add-data=ui;ui",
        "app.py"
    ]
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build completed successfully!")
        print("Your standalone executable is in: dist/APNA_Computer_RMS.exe")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")

if __name__ == "__main__":
    build()
