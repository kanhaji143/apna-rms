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
    target_name = "APNA_Computer_RMS"
    target_path = os.path.join("dist", f"{target_name}.exe")
    if os.path.exists(target_path):
        try:
            with open(target_path, "r+b"):
                pass
        except Exception:
            print(f"⚠️ {target_path} is currently running! Building as APNA_Computer_RMS_Release.exe")
            target_name = "APNA_Computer_RMS_Release"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={target_name}",
        "--onefile",
        "--windowed", # No black command prompt console
        "--noconsole",
        "--collect-all=customtkinter",
        "--version-file=file_version_info.txt",
        "--add-data=Logo.png;.",
        "--add-data=app_config.json;.",
        "--add-data=core;core",
        "--add-data=ui;ui",
        "app.py"
    ]
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build completed successfully!")
        print(f"Your standalone executable is in: dist/{target_name}.exe")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")

if __name__ == "__main__":
    build()
