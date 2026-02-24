// ========================================
// IRRIGATION SYSTEM - PROFESSIONAL JS
// Smooth real-time updates without flashing
// ========================================

// State management
let zonesState = {};
let schedulesData = [];
let historyData = [];
let currentFilter = 'all';
let updateInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌱 Irrigation System initialized');
    initializeSystem();
    startAutoUpdate();
});

// Initialize all components
function initializeSystem() {
    setDefaultDate();
    loadZones();
    loadSchedules();
    loadHistory();
    updateLastUpdateTime();
}

// Set default date to today
function setDefaultDate() {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
}

// Start auto-update every 3 seconds (faster for smooth updates)
function startAutoUpdate() {
    updateInterval = setInterval(() => {
        loadZones();
        updateSchedules();  // Changed: incremental update instead of reload
        updateHistory();    // Changed: incremental update instead of reload
        updateLastUpdateTime();
    }, 3000); // Update every 3 seconds
}

// ...existing code...

// ========================================
// SCHEDULE MANAGEMENT - OPTIMIZED
// ========================================

async function createSchedule() {
    // ...existing code...
}

async function loadSchedules() {
    try {
        const response = await fetch("/irrigation/schedule/list");
        const data = await response.json();

        schedulesData = data;
        renderSchedules(data);
    } catch (error) {
        console.error("Error loading schedules:", error);
    }
}

// NEW: Incremental schedule update - no flashing!
async function updateSchedules() {
    try {
        const response = await fetch("/irrigation/schedule/list");
        const newData = await response.json();

        // Check if data actually changed
        if (JSON.stringify(newData) === JSON.stringify(schedulesData)) {
            return; // No changes, don't re-render
        }

        // Remove items that are no longer in the new data (vencidos)
        const oldIds = schedulesData.map(s => s.id);
        const newIds = newData.map(s => s.id);

        oldIds.forEach(id => {
            if (!newIds.includes(id)) {
                const element = document.querySelector(`[data-schedule-id="${id}"]`);
                if (element) {
                    // Smooth removal animation
                    element.style.animation = 'slideOut 0.3s ease forwards';
                    setTimeout(() => element.remove(), 300);
                }
            }
        });

        // Add new items with animation
        newData.forEach(schedule => {
            const oldSchedule = schedulesData.find(s => s.id === schedule.id);
            if (!oldSchedule) {
                // New item - add it
                insertScheduleItem(schedule);
            }
        });

        schedulesData = newData;

        // Update count badge
        const countBadge = document.getElementById("scheduledCount");
        if (countBadge) {
            countBadge.textContent = newData.length;
        }

    } catch (error) {
        console.error("Error updating schedules:", error);
    }
}

function insertScheduleItem(schedule) {
    const container = document.getElementById("scheduleList");
    if (!container) return;

    // Check if empty state exists
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const sectorNames = {
        1: 'Jardín Principal',
        2: 'Huerta',
        3: 'Césped',
        4: 'Árboles'
    };

    const html = `
        <div class="schedule-item" data-schedule-id="${schedule.id}">
            <div class="schedule-info">
                <div class="schedule-detail">
                    <div class="schedule-label">Sector</div>
                    <div class="schedule-value">
                        ${schedule.sector} - ${sectorNames[schedule.sector] || 'Sector ' + schedule.sector}
                    </div>
                </div>

                <div class="schedule-detail">
                    <div class="schedule-label">Fecha</div>
                    <div class="schedule-value">${formatDate(schedule.date)}</div>
                </div>

                <div class="schedule-detail">
                    <div class="schedule-label">Horario</div>
                    <div class="schedule-value">${schedule.start_time} - ${schedule.end_time}</div>
                </div>

                <div class="schedule-detail">
                    <div class="schedule-label">Duración</div>
                    <div class="schedule-value">${calculateDuration(schedule.start_time, schedule.end_time)}</div>
                </div>
            </div>

            <div class="schedule-actions">
                <button class="btn-delete" onclick="deleteSchedule(${schedule.id})">
                    ✕ Cancelar
                </button>
            </div>
        </div>
    `;

    const temp = document.createElement('div');
    temp.innerHTML = html;
    const element = temp.firstElementChild;
    element.style.animation = 'slideIn 0.4s ease';

    container.appendChild(element);
}

function renderSchedules(schedules) {
    const container = document.getElementById("scheduleList");
    const countBadge = document.getElementById("scheduledCount");

    if (!container) return;

    if (countBadge) {
        countBadge.textContent = schedules.length;
    }

    if (schedules.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <p class="empty-state-text">No hay riegos programados</p>
            </div>
        `;
        return;
    }

    let html = '';

    schedules.forEach(schedule => {
        const sectorNames = {
            1: 'Jardín Principal',
            2: 'Huerta',
            3: 'Césped',
            4: 'Árboles'
        };

        html += `
            <div class="schedule-item" data-schedule-id="${schedule.id}">
                <div class="schedule-info">
                    <div class="schedule-detail">
                        <div class="schedule-label">Sector</div>
                        <div class="schedule-value">
                            ${schedule.sector} - ${sectorNames[schedule.sector] || 'Sector ' + schedule.sector}
                        </div>
                    </div>

                    <div class="schedule-detail">
                        <div class="schedule-label">Fecha</div>
                        <div class="schedule-value">${formatDate(schedule.date)}</div>
                    </div>

                    <div class="schedule-detail">
                        <div class="schedule-label">Horario</div>
                        <div class="schedule-value">${schedule.start_time} - ${schedule.end_time}</div>
                    </div>

                    <div class="schedule-detail">
                        <div class="schedule-label">Duración</div>
                        <div class="schedule-value">${calculateDuration(schedule.start_time, schedule.end_time)}</div>
                    </div>
                </div>

                <div class="schedule-actions">
                    <button class="btn-delete" onclick="deleteSchedule(${schedule.id})">
                        ✕ Cancelar
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

async function deleteSchedule(id) {
    if (!confirm('¿Cancelar este riego programado?')) {
        return;
    }

    try {
        const response = await fetch(`/irrigation/schedule/delete/${id}`, {
            method: "DELETE"
        });

        if (response.ok) {
            showToast("Riego cancelado", 'success');
            // Smooth removal
            const element = document.querySelector(`[data-schedule-id="${id}"]`);
            if (element) {
                element.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => {
                    element.remove();
                    // Update count
                    schedulesData = schedulesData.filter(s => s.id !== id);
                    const countBadge = document.getElementById("scheduledCount");
                    if (countBadge) {
                        countBadge.textContent = schedulesData.length;
                    }
                    if (schedulesData.length === 0) {
                        document.getElementById("scheduleList").innerHTML = `
                            <div class="empty-state">
                                <div class="empty-state-icon">📅</div>
                                <p class="empty-state-text">No hay riegos programados</p>
                            </div>
                        `;
                    }
                }, 300);
            }
        } else {
            showToast("Error al cancelar riego", 'error');
        }
    } catch (error) {
        console.error("Error deleting schedule:", error);
        showToast("Error de conexión", 'error');
    }
}

// ...existing code for clearForm...

// ========================================
// HISTORY MANAGEMENT - OPTIMIZED
// ========================================

async function loadHistory() {
    try {
        const response = await fetch("/irrigation/history/list");
        const data = await response.json();

        historyData = data;
        renderHistory(data);
    } catch (error) {
        console.error("Error loading history:", error);
    }
}

// NEW: Incremental history update - no flashing!
async function updateHistory() {
    try {
        const response = await fetch("/irrigation/history/list");
        const newData = await response.json();

        // Check if data actually changed (by comparing length and first item)
        if (newData.length === historyData.length &&
            newData[0] && historyData[0] &&
            newData[0].start_time === historyData[0].start_time) {
            return; // No changes, don't re-render
        }

        // Find new items
        newData.forEach((newRecord, index) => {
            const oldRecord = historyData[index];

            // If it's a new item at the top (EN CURSO → FINALIZADO)
            if (!oldRecord || newRecord.start_time !== oldRecord.start_time) {
                insertHistoryItem(newRecord, true); // Insert at top
            }
        });

        historyData = newData;
        applyCurrentFilter();

    } catch (error) {
        console.error("Error updating history:", error);
    }
}

function insertHistoryItem(record, atTop = true) {
    const container = document.getElementById("historyList");
    if (!container) return;

    // Remove empty state if exists
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const sectorNames = {
        1: 'Jardín Principal',
        2: 'Huerta',
        3: 'Césped',
        4: 'Árboles'
    };

    const icon = record.type === 'manual' ? '👤' : '📅';
    const typeText = record.type === 'manual' ? 'Manual' : 'Programado';

    const html = `
        <div class="history-item ${record.type}" data-history-start="${record.start_time}">
            <div class="history-icon">${icon}</div>

            <div class="history-content">
                <div class="history-field">
                    <div class="history-field-label">Sector</div>
                    <div class="history-field-value">
                        ${record.sector} - ${sectorNames[record.sector] || 'Sector ' + record.sector}
                    </div>
                </div>

                <div class="history-field">
                    <div class="history-field-label">Inicio</div>
                    <div class="history-field-value">${formatDateTime(record.start_time)}</div>
                </div>

                <div class="history-field">
                    <div class="history-field-label">Fin</div>
                    <div class="history-field-value">${record.end_time ? formatDateTime(record.end_time) : 'En curso...'}</div>
                </div>

                <div class="history-field">
                    <div class="history-field-label">Tipo</div>
                    <div class="history-field-value">${typeText}</div>
                </div>

                ${record.end_time ? `
                    <div class="history-field">
                        <div class="history-field-label">Duración</div>
                        <div class="history-field-value">${calculateTimeDiff(record.start_time, record.end_time)}</div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    const temp = document.createElement('div');
    temp.innerHTML = html;
    const element = temp.firstElementChild;
    element.style.animation = 'fadeIn 0.5s ease';

    if (atTop && container.firstChild) {
        container.insertBefore(element, container.firstChild);
    } else {
        container.appendChild(element);
    }
}

function renderHistory(history) {
    const container = document.getElementById("historyList");
    if (!container) return;

    const filteredHistory = currentFilter === 'all'
        ? history
        : history.filter(h => h.type === currentFilter);

    if (filteredHistory.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <p class="empty-state-text">No hay registros en el historial</p>
            </div>
        `;
        return;
    }

    let html = '';

    filteredHistory.forEach(record => {
        const sectorNames = {
            1: 'Jardín Principal',
            2: 'Huerta',
            3: 'Césped',
            4: 'Árboles'
        };

        const icon = record.type === 'manual' ? '👤' : '📅';
        const typeText = record.type === 'manual' ? 'Manual' : 'Programado';

        html += `
            <div class="history-item ${record.type}" data-history-start="${record.start_time}">
                <div class="history-icon">${icon}</div>

                <div class="history-content">
                    <div class="history-field">
                        <div class="history-field-label">Sector</div>
                        <div class="history-field-value">
                            ${record.sector} - ${sectorNames[record.sector] || 'Sector ' + record.sector}
                        </div>
                    </div>

                    <div class="history-field">
                        <div class="history-field-label">Inicio</div>
                        <div class="history-field-value">${formatDateTime(record.start_time)}</div>
                    </div>

                    <div class="history-field">
                        <div class="history-field-label">Fin</div>
                        <div class="history-field-value">${record.end_time ? formatDateTime(record.end_time) : 'En curso...'}</div>
                    </div>

                    <div class="history-field">
                        <div class="history-field-label">Tipo</div>
                        <div class="history-field-value">${typeText}</div>
                    </div>

                    ${record.end_time ? `
                        <div class="history-field">
                            <div class="history-field-label">Duración</div>
                            <div class="history-field-value">${calculateTimeDiff(record.start_time, record.end_time)}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function filterHistory(filter) {
    currentFilter = filter;

    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    applyCurrentFilter();
}

function applyCurrentFilter() {
    const filteredHistory = currentFilter === 'all'
        ? historyData
        : historyData.filter(h => h.type === currentFilter);

    renderHistory(filteredHistory);
}

// ...existing utility functions stay the same...

// ========================================
// ZONES MANAGEMENT
// ========================================

async function loadZones() {
    try {
        // Get zone status from backend
        const response = await fetch('/irrigation/zones/status');
        const data = await response.json();

        zonesState = data.zones || {};
        renderZones();
    } catch (error) {
        console.error('Error loading zones:', error);
        // Render default zones if error
        renderDefaultZones();
    }
}

function renderZones() {
    const container = document.getElementById('zonesGrid');
    if (!container) return;

    const zoneNames = {
        1: 'Jardín Principal',
        2: 'Huerta',
        3: 'Césped',
        4: 'Árboles'
    };

    let html = '';

    for (let i = 1; i <= 4; i++) {
        const zoneState = zonesState[i] || { active: false, duration: 0 };
        const isActive = zoneState.active;
        const duration = zoneState.duration || 0;

        html += `
            <div class="zone-card ${isActive ? 'active' : ''}" id="zone-${i}">
                <div class="zone-header">
                    <div class="zone-number">${i}</div>
                    <span class="zone-status-badge ${isActive ? 'on' : 'off'}">
                        ${isActive ? '● ACTIVO' : '○ INACTIVO'}
                    </span>
                </div>

                <div class="zone-name">${zoneNames[i]}</div>

                <div class="zone-info">
                    <div class="zone-info-item">
                        <span>⏱️</span>
                        <span>${isActive && duration > 0 ? `${Math.floor(duration / 60)}m restantes` : 'Manual'}</span>
                    </div>
                    <div class="zone-info-item">
                        <span>💧</span>
                        <span>Sector ${i}</span>
                    </div>
                </div>

                <div class="zone-actions">
                    ${isActive ? `
                        <button class="btn-zone btn-zone-off" onclick="toggleZone(${i})">
                            <span>⏸</span> Detener
                        </button>
                    ` : `
                        <button class="btn-zone btn-zone-on" onclick="toggleZone(${i})">
                            <span>▶</span> Iniciar
                        </button>
                    `}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function renderDefaultZones() {
    const container = document.getElementById('zonesGrid');
    if (!container) return;

    const zoneNames = {
        1: 'Jardín Principal',
        2: 'Huerta',
        3: 'Césped',
        4: 'Árboles'
    };

    let html = '';

    for (let i = 1; i <= 4; i++) {
        html += `
            <div class="zone-card" id="zone-${i}">
                <div class="zone-header">
                    <div class="zone-number">${i}</div>
                    <span class="zone-status-badge off">○ INACTIVO</span>
                </div>

                <div class="zone-name">${zoneNames[i]}</div>

                <div class="zone-info">
                    <div class="zone-info-item">
                        <span>⏱️</span>
                        <span>Manual</span>
                    </div>
                    <div class="zone-info-item">
                        <span>💧</span>
                        <span>Sector ${i}</span>
                    </div>
                </div>

                <div class="zone-actions">
                    <button class="btn-zone btn-zone-on" onclick="toggleZone(${i})">
                        <span>▶</span> Iniciar
                    </button>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

async function toggleZone(zoneId) {
    try {
        // Disable button to prevent double clicks
        const zoneCard = document.getElementById(`zone-${zoneId}`);
        if (zoneCard) {
            zoneCard.style.opacity = '0.6';
            zoneCard.style.pointerEvents = 'none';
        }

        const response = await fetch(`/irrigation/manual/${zoneId}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            showToast(`Zona ${zoneId} ${data.active ? 'activada' : 'desactivada'}`, 'success');

            // Immediate update
            setTimeout(() => {
                loadZones();
            }, 500);
        } else {
            showToast('Error al controlar la zona', 'error');
        }

        // Re-enable after a moment
        setTimeout(() => {
            if (zoneCard) {
                zoneCard.style.opacity = '1';
                zoneCard.style.pointerEvents = 'auto';
            }
        }, 1000);

    } catch (error) {
        console.error('Error toggling zone:', error);
        showToast('Error de conexión', 'error');
    }
}

async function emergencyStop() {
    if (!confirm('¿Detener TODAS las zonas de riego inmediatamente?')) {
        return;
    }

    try {
        const response = await fetch('/irrigation/emergency-stop', {
            method: 'POST'
        });

        if (response.ok) {
            showToast('🚨 TODAS las zonas han sido detenidas', 'warning');
            loadZones();
        } else {
            showToast('Error al ejecutar parada de emergencia', 'error');
        }
    } catch (error) {
        console.error('Error in emergency stop:', error);
        showToast('Error de conexión', 'error');
    }
}

// ========================================
// SCHEDULE MANAGEMENT
// ========================================

async function createSchedule() {
    const sectorEl = document.getElementById("sector");
    const dateEl = document.getElementById("date");
    const startEl = document.getElementById("time");
    const endEl = document.getElementById("end_time");

    if (!sectorEl || !dateEl || !startEl || !endEl) {
        console.error("Missing form elements");
        return;
    }

    const sector = sectorEl.value;
    const date = dateEl.value;
    const start_time = startEl.value;
    const end_time = endEl.value;

    if (!sector || !date || !start_time || !end_time) {
        showToast("Por favor completa todos los campos", 'warning');
        return;
    }

    if (end_time <= start_time) {
        showToast("La hora de fin debe ser posterior a la hora de inicio", 'warning');
        return;
    }

    try {
        const response = await fetch("/irrigation/schedule/add", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                sector,
                date,
                start_time,
                end_time
            })
        });

        if (response.ok) {
            showToast("✓ Riego programado correctamente", 'success');
            clearForm();
            loadSchedules();
        } else {
            const error = await response.json();
            showToast("Error al programar riego: " + (error.error || 'Unknown'), 'error');
        }
    } catch (error) {
        console.error("Error creating schedule:", error);
        showToast("Error de conexión", 'error');
    }
}

async function loadSchedules() {
    try {
        const response = await fetch("/irrigation/schedule/list");
        const data = await response.json();

        schedulesData = data;
        renderSchedules(data);
    } catch (error) {
        console.error("Error loading schedules:", error);
    }
}

function renderSchedules(schedules) {
    const container = document.getElementById("scheduleList");
    const countBadge = document.getElementById("scheduledCount");

    if (!container) return;

    if (countBadge) {
        countBadge.textContent = schedules.length;
    }

    if (schedules.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <p class="empty-state-text">No hay riegos programados</p>
            </div>
        `;
        return;
    }

    let html = '';

    schedules.forEach(schedule => {
        const sectorNames = {
            1: 'Jardín Principal',
            2: 'Huerta',
            3: 'Césped',
            4: 'Árboles'
        };

        html += `
            <div class="schedule-item">
                <div class="schedule-info">
                    <div class="schedule-detail">
                        <div class="schedule-label">Sector</div>
                        <div class="schedule-value">
                            ${schedule.sector} - ${sectorNames[schedule.sector] || 'Sector ' + schedule.sector}
                        </div>
                    </div>

                    <div class="schedule-detail">
                        <div class="schedule-label">Fecha</div>
                        <div class="schedule-value">${formatDate(schedule.date)}</div>
                    </div>

                    <div class="schedule-detail">
                        <div class="schedule-label">Horario</div>
                        <div class="schedule-value">${schedule.start_time} - ${schedule.end_time}</div>
                    </div>

                    <div class="schedule-detail">
                        <div class="schedule-label">Duración</div>
                        <div class="schedule-value">${calculateDuration(schedule.start_time, schedule.end_time)}</div>
                    </div>
                </div>

                <div class="schedule-actions">
                    <button class="btn-delete" onclick="deleteSchedule(${schedule.id})">
                        ✕ Cancelar
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

async function deleteSchedule(id) {
    if (!confirm('¿Cancelar este riego programado?')) {
        return;
    }

    try {
        const response = await fetch(`/irrigation/schedule/delete/${id}`, {
            method: "DELETE"
        });

        if (response.ok) {
            showToast("Riego cancelado", 'success');
            loadSchedules();
        } else {
            showToast("Error al cancelar riego", 'error');
        }
    } catch (error) {
        console.error("Error deleting schedule:", error);
        showToast("Error de conexión", 'error');
    }
}

function clearForm() {
    const dateEl = document.getElementById("date");
    const startEl = document.getElementById("time");
    const endEl = document.getElementById("end_time");
    const sectorEl = document.getElementById("sector");

    if (sectorEl) sectorEl.value = "1";
    if (dateEl) dateEl.value = new Date().toISOString().split('T')[0];
    if (startEl) startEl.value = "";
    if (endEl) endEl.value = "";
}

// ========================================
// HISTORY MANAGEMENT
// ========================================

async function loadHistory() {
    try {
        const response = await fetch("/irrigation/history/list");
        const data = await response.json();

        historyData = data;
        renderHistory(data);
    } catch (error) {
        console.error("Error loading history:", error);
    }
}

function renderHistory(history) {
    const container = document.getElementById("historyList");
    if (!container) return;

    const filteredHistory = currentFilter === 'all'
        ? history
        : history.filter(h => h.type === currentFilter);

    if (filteredHistory.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <p class="empty-state-text">No hay registros en el historial</p>
            </div>
        `;
        return;
    }

    let html = '';

    filteredHistory.forEach(record => {
        const sectorNames = {
            1: 'Jardín Principal',
            2: 'Huerta',
            3: 'Césped',
            4: 'Árboles'
        };

        const icon = record.type === 'manual' ? '👤' : '📅';
        const typeText = record.type === 'manual' ? 'Manual' : 'Programado';

        html += `
            <div class="history-item ${record.type}">
                <div class="history-icon">${icon}</div>

                <div class="history-content">
                    <div class="history-field">
                        <div class="history-field-label">Sector</div>
                        <div class="history-field-value">
                            ${record.sector} - ${sectorNames[record.sector] || 'Sector ' + record.sector}
                        </div>
                    </div>

                    <div class="history-field">
                        <div class="history-field-label">Inicio</div>
                        <div class="history-field-value">${formatDateTime(record.start_time)}</div>
                    </div>

                    <div class="history-field">
                        <div class="history-field-label">Fin</div>
                        <div class="history-field-value">${record.end_time ? formatDateTime(record.end_time) : 'En curso...'}</div>
                    </div>

                    <div class="history-field">
                        <div class="history-field-label">Tipo</div>
                        <div class="history-field-value">${typeText}</div>
                    </div>

                    ${record.end_time ? `
                        <div class="history-field">
                            <div class="history-field-label">Duración</div>
                            <div class="history-field-value">${calculateTimeDiff(record.start_time, record.end_time)}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function filterHistory(filter) {
    currentFilter = filter;

    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    renderHistory(historyData);
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('es-ES', options);
}

function formatDateTime(dateTimeString) {
    if (!dateTimeString) return '-';
    const date = new Date(dateTimeString);
    const dateOptions = { month: 'short', day: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('es-ES', dateOptions) + ' ' +
           date.toLocaleTimeString('es-ES', timeOptions);
}

function calculateDuration(startTime, endTime) {
    const [startHour, startMin] = startTime.split(':').map(Number);
    const [endHour, endMin] = endTime.split(':').map(Number);

    const startMinutes = startHour * 60 + startMin;
    const endMinutes = endHour * 60 + endMin;
    const diffMinutes = endMinutes - startMinutes;

    if (diffMinutes < 60) {
        return `${diffMinutes} min`;
    } else {
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return minutes > 0 ? `${hours}h ${minutes}min` : `${hours}h`;
    }
}

function calculateTimeDiff(startDateTime, endDateTime) {
    if (!startDateTime || !endDateTime) return '-';

    const start = new Date(startDateTime);
    const end = new Date(endDateTime);
    const diffMs = end - start;
    const diffMinutes = Math.floor(diffMs / 60000);

    if (diffMinutes < 60) {
        return `${diffMinutes} min`;
    } else {
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return minutes > 0 ? `${hours}h ${minutes}min` : `${hours}h`;
    }
}

function showToast(message, type = 'success') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success' ? '✓' :
                 type === 'error' ? '✕' :
                 type === 'warning' ? '⚠' : 'ℹ';

    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;

    document.body.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInUp 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});

console.log('✓ Irrigation system ready');
