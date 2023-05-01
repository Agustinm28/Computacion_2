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

# Ruta completa al archivo 'activate' en el directorio del entorno virtual
subprocess.run(["source", "env.sh"], check=True)

# Install dependencies and project package
# subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
