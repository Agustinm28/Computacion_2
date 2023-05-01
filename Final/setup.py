import os
import platform
import subprocess

# Check if virtual environment exists
if os.path.exists(os.path.join(os.getcwd(), 'env')):
    print("Found existing virtual environment.")
else:
    # Create virtual environment
    subprocess.run(["python3", "-m", "venv", "env"], check=True)
    print("Created new virtual environment.")

# Activate virtual environment
if platform.system() == "Windows":
    activate_command = os.path.join("env", "Scripts", "activate.bat")
elif platform.system() == "Darwin":  # Mac OS
    activate_command = os.path.join("env", "bin", "activate")
else:
    activate_command = os.path.join("env", "bin", "activate")
subprocess.run([activate_command], check=True, shell=True)

# Install dependencies and project package
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)