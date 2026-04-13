#!/bin/bash

# ESP32 WROOM LoRa Irrigation System - Installation Script
# Uses EBYTE E220/E32 UART LoRa module for RPi <-> ESP32 communication

echo "================================================"
echo "  ESP32 WROOM LoRa Irrigation System - RPI Setup"
echo "  (EBYTE UART LoRa Module)"
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

echo "Step 1: Checking UART interface..."
if ls /dev/serial0 2>/dev/null || ls /dev/ttyAMA0 2>/dev/null; then
    echo "✅ UART is available"
else
    echo "❌ UART is not enabled"
    echo "Please enable UART:"
    echo "  sudo raspi-config"
    echo "  → Interface Options → Serial Port"
    echo "  → Login shell: No"
    echo "  → Hardware serial: Yes"
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
echo "Step 4: Installing Python LoRa UART dependencies..."
pip3 install pyserial RPi.GPIO
echo "✅ pyserial and RPi.GPIO installed"

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

