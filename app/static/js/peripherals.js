// ========================================
// PERIPHERALS STATUS PAGE
// Real-time hardware monitoring
// ========================================

let periphData = [];
let periphInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔌 Peripherals monitor initialized');
    loadPeripherals();
    // Auto-refresh every 10 seconds
    periphInterval = setInterval(loadPeripherals, 10000);
});

// Icon map per device type
const DEVICE_ICONS = {
    relay: '⚡',
    sensor: '🌡️',
    actuator: '💉',
    esp32: '📡',
    system: '💾'
};

// Status labels
const STATUS_LABELS = {
    ok: { text: 'OPERATIVO', class: 'label-ok' },
    active: { text: 'ACTIVO', class: 'label-active' },
    idle: { text: 'EN REPOSO', class: 'label-idle' },
    error: { text: 'ERROR', class: 'label-error' },
    unknown: { text: 'DESCONOCIDO', class: 'label-unknown' }
};

async function loadPeripherals() {
    try {
        const response = await fetch('/api/peripherals/status');
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const data = await response.json();

        // Only re-render if data changed
        const dataStr = JSON.stringify(data);
        if (dataStr === JSON.stringify(periphData)) {
            updateTimestamp();
            return;
        }

        periphData = data;
        renderPeripherals(data);
        updateSummary(data);
        updatePumpStatus(data);
        updateTimestamp();

    } catch (error) {
        console.error('Error loading peripherals:', error);
    }
}

function refreshPeripherals() {
    const btn = document.getElementById('btnRefresh');
    if (btn) {
        btn.classList.add('loading');
        btn.textContent = '⏳ Comprobando...';
    }

    loadPeripherals().finally(() => {
        setTimeout(() => {
            if (btn) {
                btn.classList.remove('loading');
                btn.textContent = '🔄 Actualizar';
            }
        }, 800);
    });
}

function renderPeripherals(devices) {
    const grid = document.getElementById('periphGrid');
    if (!grid) return;

    if (!devices || devices.length === 0) {
        grid.innerHTML = `
            <div class="periph-loading">
                <p>No se encontraron periféricos configurados</p>
            </div>
        `;
        return;
    }

    let html = '';

    devices.forEach(device => {
        const icon = DEVICE_ICONS[device.type] || '❓';
        const statusInfo = STATUS_LABELS[device.status] || STATUS_LABELS.unknown;
        const dotClass = `dot-${device.status || 'unknown'}`;
        const cardClass = `status-${device.status || 'unknown'}`;

        html += `
            <div class="periph-card ${cardClass}" data-device-id="${device.id}">
                <div class="periph-card-header">
                    <div>
                        <div class="periph-card-name">${device.name}</div>
                        <div class="periph-card-type">${device.type}</div>
                    </div>
                    <div style="display:flex;align-items:center;gap:0.5rem;">
                        <span class="periph-status-label ${statusInfo.class}">
                            <span class="status-dot ${dotClass}"></span>
                            ${statusInfo.text}
                        </span>
                    </div>
                </div>

                <div class="periph-card-icon">${icon}</div>

                <div class="periph-card-message">${device.message || '-'}</div>

                <div class="periph-card-footer">
                    <span class="periph-card-detail">${device.detail || ''}</span>
                    <span>Visto: ${formatTimestamp(device.last_seen)}</span>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
}

function updateSummary(devices) {
    let ok = 0, active = 0, idle = 0, error = 0;

    devices.forEach(d => {
        switch (d.status) {
            case 'ok': ok++; break;
            case 'active': active++; break;
            case 'idle': idle++; break;
            case 'error': error++; break;
        }
    });

    const setCount = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    setCount('countOk', ok);
    setCount('countActive', active);
    setCount('countIdle', idle);
    setCount('countError', error);
}

function updatePumpStatus(devices) {
    const pump = devices.find(d => d.id === 'pump');
    if (!pump) return;

    const indicator = document.querySelector('.pump-indicator');
    const statusText = document.getElementById('pumpStatusText');

    if (pump.status === 'active') {
        if (indicator) { indicator.className = 'pump-indicator on'; }
        if (statusText) { statusText.textContent = 'Inyectando fertilizante'; statusText.style.color = '#22c55e'; }
    } else {
        if (indicator) { indicator.className = 'pump-indicator off'; }
        if (statusText) { statusText.textContent = 'Apagada'; statusText.style.color = '#6b7280'; }
    }
}

function updateTimestamp() {
    const el = document.getElementById('periphLastUpdate');
    if (el) {
        const now = new Date();
        el.textContent = `Última comprobación: ${now.toLocaleTimeString('es-ES')}`;
    }
}

function formatTimestamp(ts) {
    if (!ts) return '-';
    try {
        const d = new Date(ts);
        return d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    } catch {
        return ts;
    }
}

// --- Pump Control ---
async function pumpOn() {
    const btn = document.getElementById('btnPumpOn');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ Encendiendo...'; }

    try {
        const response = await fetch('/api/pump/on', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ duration: 300 }) // 5 minutes
        });

        const result = await response.json();
        if (result.success) {
            showPeriphToast('✅ ' + result.message, 'success');
            loadPeripherals();
        } else {
            showPeriphToast('❌ ' + (result.error || 'Error'), 'error');
        }
    } catch (error) {
        showPeriphToast('❌ Error de conexión', 'error');
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '▶ Encender Bomba (5 min)'; }
    }
}

async function pumpOff() {
    const btn = document.getElementById('btnPumpOff');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ Apagando...'; }

    try {
        const response = await fetch('/api/pump/off', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();
        if (result.success) {
            showPeriphToast('✅ ' + result.message, 'success');
            loadPeripherals();
        } else {
            showPeriphToast('❌ ' + (result.error || 'Error'), 'error');
        }
    } catch (error) {
        showPeriphToast('❌ Error de conexión', 'error');
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '⏸ Apagar Bomba'; }
    }
}

function showPeriphToast(message, type) {
    // Remove existing
    document.querySelectorAll('.periph-toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `periph-toast periph-toast-${type}`;
    toast.style.cssText = `
        position: fixed; bottom: 2rem; right: 2rem; z-index: 9999;
        padding: 0.8rem 1.5rem; border-radius: 10px; font-weight: 600;
        font-size: 0.9rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        animation: slideUp 0.3s ease;
        color: white;
        background: ${type === 'success' ? '#22c55e' : '#ef4444'};
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Cleanup
window.addEventListener('beforeunload', () => {
    if (periphInterval) clearInterval(periphInterval);
});

