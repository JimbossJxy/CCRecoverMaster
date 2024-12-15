#!/bin/bash

# Configuration
PYTHON_VERSION="3.12.7"
APP_DIR="/home/masterNode"  # Replace with the directory containing main.py
SERVICE_NAME="main_app"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo."
    exit 1
fi

# Function to run a command and exit on failure
run_command() {
    echo "Running: $1"
    eval "$1"
    if [ $? -ne 0 ]; then
        echo "Command failed: $1"
        exit 1
    fi
}

# Step 1: Install system dependencies
echo "Installing system dependencies..."
run_command "apt update -y"
run_command "apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev"

# Step 2: Download and install Python 3.12.7
if ! python3.12 --version &>/dev/null; then
    echo "Installing Python $PYTHON_VERSION..."
    run_command "cd /usr/src && wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
    run_command "cd /usr/src && tar xzf Python-$PYTHON_VERSION.tgz"
    run_command "cd /usr/src/Python-$PYTHON_VERSION && ./configure --enable-optimizations"
    run_command "cd /usr/src/Python-$PYTHON_VERSION && make -j$(nproc)"
    run_command "cd /usr/src/Python-$PYTHON_VERSION && make altinstall"
else
    echo "Python $PYTHON_VERSION is already installed."
fi

# Step 3: Install Python dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing Python dependencies from $REQUIREMENTS_FILE..."
    run_command "python3.12 -m ensurepip --upgrade"
    run_command "python3.12 -m pip install --upgrade pip"
    run_command "python3.12 -m pip install -r $REQUIREMENTS_FILE"
else
    echo "Requirements file not found: $REQUIREMENTS_FILE"
    exit 1
fi

# Step 4: Create systemd service
echo "Setting up $SERVICE_NAME as a systemd service..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
cat <<EOL >$SERVICE_FILE
[Unit]
Description=Python App - Main Script
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/python3.12 $APP_DIR/main.py
Restart=always
User=$(whoami)
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

run_command "systemctl daemon-reload"
run_command "systemctl enable $SERVICE_NAME"

# Step 5: Start the service
echo "Starting $SERVICE_NAME service..."
run_command "systemctl start $SERVICE_NAME"

# Check service status
systemctl status $SERVICE_NAME --no-pager

echo "Setup complete! The app will now start automatically on boot."
