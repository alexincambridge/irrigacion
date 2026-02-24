#!/bin/bash

# ESP32 LoRa Irrigation System - Installation Script
# This script helps automate the Raspberry Pi setup

echo "================================================"
echo "  ESP32 LoRa Irrigation System - RPI Setup"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Checking SPI interface..."
if lsmod | grep -q spi_bcm2835; then
    echo "✅ SPI is enabled"
else
    echo "❌ SPI is not enabled"
    echo "Please enable SPI:"
    echo "  sudo raspi-config"
    echo "  → Interface Options → SPI → Enable"
    echo "  → Reboot"
    exit 1
fi

echo ""
echo "Step 2: Checking Python version..."
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python 3 is installed"
else
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo ""
echo "Step 3: Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev git libgpiod2

echo ""
echo "Step 4: Installing Python LoRa library..."
echo "Choose installation method:"
echo "  1) Install from GitHub (recommended)"
echo "  2) Skip (already installed)"
read -r choice

if [ "$choice" = "1" ]; then
    cd ~
    if [ -d "pySX127x" ]; then
        echo "pySX127x directory already exists, removing..."
        rm -rf pySX127x
    fi
    git clone https://github.com/mayeranalytics/pySX127x.git
    cd pySX127x
    sudo python3 setup.py install
    echo "✅ LoRa library installed"
fi

echo ""
echo "Step 5: Installing project dependencies..."
cd /Users/alexg/Sites/irrigacion
pip3 install -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "Step 6: Checking configuration..."
if grep -q "HARDWARE_MODE = 'LORA'" app/config.py; then
    echo "✅ Hardware mode is set to LoRa"
else
    echo "⚠️  Hardware mode is not set to LoRa"
    echo "Please edit app/config.py and set:"
    echo "  HARDWARE_MODE = 'LORA'"
fi

echo ""
echo "Step 7: Testing LoRa connection..."
echo "Ready to test? This will check if ESP32 is responding."
echo "Make sure ESP32 is powered on and code is uploaded."
echo "Continue with test? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    python3 scripts/test_lora.py
else
    echo "Skipping test. You can run it later with:"
    echo "  python3 scripts/test_lora.py"
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. If tests failed, check wiring and ESP32 code"
echo "  2. Start Flask app: python run.py"
echo "  3. Access web interface: http://localhost:5000"
echo ""
echo "Documentation:"
echo "  - Quick Start: ESP32_QUICKSTART.md"
echo "  - Full Guide: ESP32/SETUP_GUIDE.md"
echo "  - Wiring: ESP32/WIRING_DIAGRAMS.md"
echo ""
echo "Happy irrigating! 💧🌱"

