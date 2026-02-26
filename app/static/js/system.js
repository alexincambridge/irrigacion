// ============================================
// SYSTEM PAGE - PROFESSIONAL JS
// Network info, ESP32 devices, departments
// ============================================

console.log('💻 System Page initialized');

let updateInterval = null;
let startTime = Date.now();

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('System page loaded');

    // Load initial data
    checkInternetConnection();
    loadESP32Devices();
    loadSystemInfo();
    updateUptime();

    // Auto-refresh every 10 seconds
    updateInterval = setInterval(() => {
        checkInternetConnection();
        loadESP32Devices();
        updateUptime();
    }, 10000);
});

// ============================================
// INTERNET CONNECTION CHECK
// ============================================

async function checkInternetConnection() {
    try {
        const response = await fetch('/system/internet-check');
        const data = await response.json();

        const statusBadge = document.getElementById('internetStatus');
        const connectionStatus = document.getElementById('internetConnectionStatus');
        const publicIPEl = document.getElementById('publicIP');
        const ispNameEl = document.getElementById('ispName');

        if (data.connected) {
            statusBadge.className = 'status-badge online';
            statusBadge.innerHTML = '<span class="status-dot"></span> Online';

            connectionStatus.innerHTML = `
                <span class="status-indicator">✓</span>
                <span class="status-text">Conectado</span>
            `;

            publicIPEl.textContent = data.public_ip || '--';
            ispNameEl.textContent = data.isp || '--';
        } else {
            statusBadge.className = 'status-badge offline';
            statusBadge.innerHTML = '<span class="status-dot"></span> Offline';

            connectionStatus.innerHTML = `
                <span class="status-indicator">✗</span>
                <span class="status-text">Sin conexión</span>
            `;

            publicIPEl.textContent = '--';
            ispNameEl.textContent = '--';
        }

    } catch (error) {
        console.error('Error checking internet:', error);

        const statusBadge = document.getElementById('internetStatus');
        statusBadge.className = 'status-badge offline';
        statusBadge.innerHTML = '<span class="status-dot"></span> Error';
    }
}

// ============================================
// ESP32 DEVICES
// ============================================

async function loadESP32Devices() {
    try {
        const response = await fetch('/system/esp32-devices');
        const data = await response.json();

        const devicesGrid = document.getElementById('esp32DevicesGrid');
        const countBadge = document.getElementById('esp32Count');

        if (!data.devices || data.devices.length === 0) {
            devicesGrid.innerHTML = `
                <div class="loading-devices">
                    <p style="font-size: 2rem;">📡</p>
                    <p>No se encontraron dispositivos ESP32</p>
                    <p style="font-size: 0.875rem; color: #9ca3af;">
                        Verifica que los dispositivos estén encendidos y conectados a la red
                    </p>
                </div>
            `;
            countBadge.textContent = '0 conectados';
            return;
        }

        countBadge.textContent = `${data.devices.length} conectado${data.devices.length !== 1 ? 's' : ''}`;

        let html = '';
        data.devices.forEach(device => {
            const statusClass = device.online ? 'online' : 'offline';
            const statusText = device.online ? 'Online' : 'Offline';

            html += `
                <div class="device-card ${statusClass}">
                    <div class="device-header">
                        <div class="device-name">📡 ${device.name}</div>
                        <div class="device-status ${statusClass}">${statusText}</div>
                    </div>
                    <div class="device-info">
                        <div class="device-info-row">
                            <span class="device-info-label">IP:</span>
                            <span class="device-info-value">${device.ip}</span>
                        </div>
                        <div class="device-info-row">
                            <span class="device-info-label">MAC:</span>
                            <span class="device-info-value">${device.mac || '--'}</span>
                        </div>
                        <div class="device-info-row">
                            <span class="device-info-label">Zonas:</span>
                            <span class="device-info-value">${device.zones || 4}</span>
                        </div>
                        <div class="device-info-row">
                            <span class="device-info-label">Última comunicación:</span>
                            <span class="device-info-value">${device.last_seen || 'Ahora'}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        devicesGrid.innerHTML = html;

    } catch (error) {
        console.error('Error loading ESP32 devices:', error);

        const devicesGrid = document.getElementById('esp32DevicesGrid');
        devicesGrid.innerHTML = `
            <div class="loading-devices">
                <p style="font-size: 2rem;">⚠️</p>
                <p>Error al cargar dispositivos</p>
            </div>
        `;
    }
}

// ============================================
// SYSTEM INFO
// ============================================

async function loadSystemInfo() {
    try {
        // Load water consumption
        const waterResponse = await fetch('/system/water-total');
        const waterData = await waterResponse.json();

        const waterTotalEl = document.getElementById('waterTotal');
        if (waterTotalEl && waterData.total !== undefined) {
            waterTotalEl.textContent = `${waterData.total.toFixed(1)} L`;
        }

        // Load logs count
        const logsResponse = await fetch('/system/logs-count');
        const logsData = await logsResponse.json();

        const logsCountEl = document.getElementById('logsCount');
        if (logsCountEl && logsData.count !== undefined) {
            logsCountEl.textContent = logsData.count;
        }

    } catch (error) {
        console.error('Error loading system info:', error);
    }
}

// ============================================
// UPTIME CALCULATOR
// ============================================

function updateUptime() {
    const now = Date.now();
    const elapsed = now - startTime;

    const seconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    let uptimeText = '';
    if (days > 0) {
        uptimeText = `${days}d ${hours % 24}h ${minutes % 60}m`;
    } else if (hours > 0) {
        uptimeText = `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
        uptimeText = `${minutes}m ${seconds % 60}s`;
    } else {
        uptimeText = `${seconds}s`;
    }

    const uptimeEl = document.getElementById('uptime');
    if (uptimeEl) {
        uptimeEl.textContent = uptimeText;
    }
}

// ============================================
// CLEANUP
// ============================================

window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});

