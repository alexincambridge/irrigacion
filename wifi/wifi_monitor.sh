#!/bin/bash

KNOWN_SSID="TuWiFiCasa"
CHECK_INTERVAL=20

start_ap() {
    echo "Activando modo Access Point..."

    systemctl stop wpa_supplicant
    ip link set wlan0 down
    ip addr flush dev wlan0
    ip link set wlan0 up
    ip addr add 192.168.4.1/24 dev wlan0

    systemctl start dnsmasq
    systemctl start hostapd
}

stop_ap() {
    echo "Conectado a WiFi. Desactivando AP..."

    systemctl stop hostapd
    systemctl stop dnsmasq

    ip link set wlan0 down
    ip addr flush dev wlan0
    ip link set wlan0 up

    systemctl start wpa_supplicant
}

while true; do
    CURRENT_SSID=$(iwgetid -r)

    if [ "$CURRENT_SSID" = "$KNOWN_SSID" ]; then
        if systemctl is-active --quiet hostapd; then
            stop_ap
        fi
    else
        if ! systemctl is-active --quiet hostapd; then
            start_ap
        fi
    fi

    sleep $CHECK_INTERVAL
done
# da permisos
# sudo chmod +x /usr/local/bin/wifi_monitor.sh
# sudo nano /etc/systemd/system/wifi-monitor.service

