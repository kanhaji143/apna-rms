import os
import subprocess
import sys
import shutil

def main():
    print("🚀 Step 1: Building PyInstaller onedir binaries...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=APNA_Computer_RMS_Portable",
        "--onedir",
        "--windowed",
        "--noconsole",
        "--icon=app_icon.ico",
        "--collect-all=customtkinter",
        "--collect-all=playwright",
        "--version-file=file_version_info.txt",
        "--add-data=Logo.png;.",
        "--add-data=app_config.json;.",
        "--add-data=fonts;fonts",
        "--distpath=build/app_binaries_dist",
        "--noconfirm",
        "app.py"
    ]
    subprocess.run(cmd, check=True)

    print("🚀 Step 2: Syncing build/app_binaries...")
    built_dir = os.path.join("build", "app_binaries_dist", "APNA_Computer_RMS_Portable")
    target_dir = os.path.join("build", "app_binaries")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.move(built_dir, target_dir)
    print("Synced binaries successfully!")

    print("🚀 Step 3: Compiling Inno Setup Installer...")
    iscc = r"C:\Users\A\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    subprocess.run([iscc, "installer_setup.iss"], check=True)

    print("\n✅ Build and Packaging Complete!")
    setup_exe = os.path.join("dist", "APNA_Computer_RMS_Setup.exe")
    if os.path.exists(setup_exe):
        sz = os.path.getsize(setup_exe)
        print(f"Final Setup File: {setup_exe} ({sz:,} bytes)")

if __name__ == "__main__":
    main()
