#!/bin/bash

# Variables
PYTHON_VERSION="3.12.7"
APP_DIR="/home/masterNode"  # Replace with the directory containing main.py
SERVICE_NAME="MasterNodeService"     # Name of the service

echo "Starting setup..."

# Step 1: Update and install dependencies
sudo apt update -y
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git

# Step 2: Install Python 3.12.7
if ! python3.12 --version &>/dev/null; then
    echo "Installing Python $PYTHON_VERSION..."
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
    sudo tar xzf Python-$PYTHON_VERSION.tgz
    cd Python-$PYTHON_VERSION
    sudo ./configure --enable-optimizations
    sudo make altinstall
else
    echo "Python $PYTHON_VERSION is already installed."
fi

# Verify Python installation
if python3.12 --version &>/dev/null; then
    echo "Python $(python3.12 --version) installed successfully."
else
    echo "Python installation failed. Exiting..."
    exit 1
fi

# Step 3: Install pip and requirements
echo "Installing pip and requirements..."
sudo python3.12 -m ensurepip --upgrade
sudo python3.12 -m pip install --upgrade pip
sudo python3.12 -m pip install -r $APP_DIR/requirements.txt

# Step 4: Create a systemd service for main.py
echo "Setting up $SERVICE_NAME as a systemd service..."

SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
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

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# Start the service
echo "Starting $SERVICE_NAME service..."
sudo systemctl start $SERVICE_NAME

# Check service status
sudo systemctl status $SERVICE_NAME --no-pager

echo "Setup complete! The app will now start automatically on boot."
