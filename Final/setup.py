import os
import platform
import subprocess

# Update and upgrade
print('[INSTALL] Updating and upgrading')
try:
    subprocess.run(["sudo", "apt-get", "update", "-y"])
    subprocess.run(["sudo", "apt-get", "upgrade", "-y"])
except Exception as e:
    print(f'[ERROR] Update and upgrade failed. {e}')

# Install OpenCV and ffmpeg
try:
    print('[INSTALL] Installing OpenCV')
    result = subprocess.run(["dpkg-query", "-W", "-f='${Status}'", "python3-opencv"], capture_output=True, text=True)
    if "install ok installed" in result.stdout:
        print("[INSTALLED] OpenCV is already installed")
    else:
        subprocess.run(["sudo", "apt-get", "install", "-y", "python3-opencv"])
except Exception as e:
    print(f'[ERROR] OpenCV install failed. {e}')

try:
    result = subprocess.run(["dpkg-query", "-W", "-f='${Status}'", "ffmpeg"], capture_output=True, text=True)
    if "install ok installed" in result.stdout:
        print("[INSTALLED] ffmpeg is already installed")
    else:
        subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"])
except Exception as e:
    print(f'[ERROR] ffmpeg install failed. {e}')

# Add OpenCV to PATH
try:
    print('[INSTALL] Adding OpenCV to PATH')
    filename = os.path.expanduser("~/.bashrc")
    with open(filename, "a") as f:
        f.write("\n")
        f.write("export PYTHONPATH=/usr/local/lib/python3.10/site-packages:$PYTHONPATH")
except Exception as e:
    print(f'[ERROR] OpenCV PATH adding failed. {e}')

# Install dependencies and project package
try:
    print('[INSTALL] Installing dependencies')
    result = subprocess.run(["dpkg-query", "-W", "-f='${Status}'", "pip"], capture_output=True, text=True)
    if "install ok installed" in result.stdout:
        pass
    else:
        subprocess.run(["sudo", "apt-get", "install", "-y", "pip"])
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
except Exception as e:
    print(f'[ERROR] Dependencies install failed. {e}')
