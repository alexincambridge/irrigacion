// ========================================
// INDUSTRIAL DASHBOARD - PROFESSIONAL JS
// Dynamic gauges with criticality colors
// ========================================

console.log("🏭 Industrial Dashboard initialized");

// State management
let dailyStats = {
  temperature: { min: null, max: null, values: [] },
  humidity: { min: null, max: null, values: [] },
  pressure: { min: null, max: null, values: [] },
  solar: { min: null, max: null, values: [] },
  waterPressure: { min: null, max: null, values: [] },
  ph: { min: null, max: null, values: [] },
  ec: { min: null, max: null, values: [] }
};

let gauges = {};
let historyChart = null;
let visibleSensors = ['temp', 'humidity', 'pressure', 'solar'];

// Criticality thresholds
const thresholds = {
  temperature: {
    critical: { min: 5, max: 40 },
    warning: { min: 10, max: 35 },
    normal: { min: 15, max: 30 }
  },
  humidity: {
    critical: { min: 20, max: 90 },
    warning: { min: 30, max: 80 },
    normal: { min: 40, max: 70 }
  },
  pressure: {
    critical: { min: 980, max: 1040 },
    warning: { min: 990, max: 1030 },
    normal: { min: 1000, max: 1020 }
  },
  solar: {
    warning: { max: 800 },
    critical: { max: 1000 }
  },
  waterPressure: {
    critical: { min: 0.5, max: 6 },
    warning: { min: 1, max: 5 },
    normal: { min: 1.5, max: 4 }
  },
  ph: {
    critical: { min: 5.5, max: 8.5 },
    warning: { min: 6, max: 8 },
    normal: { min: 6.5, max: 7.5 }
  },
  ec: {
    critical: { min: 0.5, max: 2.5 },
    warning: { min: 0.8, max: 2 },
    normal: { min: 1, max: 1.8 }
  }
};

// Color schemes for criticality
const colors = {
  normal: ['#22c55e', '#16a34a'],
  warning: ['#f59e0b', '#d97706'],
  critical: ['#ef4444', '#dc2626']
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
  initializeGauges();
  initializeChart();
  loadHistoricalData();
  refresh();
  setInterval(refresh, 5000);

  // Reset daily stats at midnight
  scheduleResetDailyStats();
});

// ========================================
// GAUGE INITIALIZATION
// ========================================

function refresh() {
  loadDashboardData();
  loadHistoricalData();
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
  initializeGauges();
  initializeChart();
  loadDashboardData(); // Carga inicial
  loadHistoricalData();
  setInterval(refresh, 5000);

function createGauge(elementId, config) {
  const element = document.querySelector(`#${elementId}`);
  if (!element) return null;

  const options = {
    chart: {
      type: 'radialBar',
      height: config.height || 280,
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800
      }
    },
    series: [0],
    colors: [colors.normal[0]],
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 135,
        hollow: {
          size: '65%',
          background: 'transparent'
        },
        track: {
          background: '#f1f5f9',
          strokeWidth: '100%',
          margin: 5
        },
        dataLabels: {
          name: {
            fontSize: config.height === 120 ? '11px' : '14px',
            color: '#6b7280',
            offsetY: -5
          },
          value: {
            fontSize: config.height === 120 ? '20px' : '32px',
            fontWeight: 700,
            color: '#1f2937',
            offsetY: 2,
            formatter: function(val) {
              const actual = (val / 100) * (config.max - config.min) + config.min;
              return actual.toFixed(config.type === 'ec' || config.type === 'ph' ? 1 : 1);
            }
          }
        }
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
        shade: 'dark',
        type: 'horizontal',
        shadeIntensity: 0.5,
        gradientToColors: [colors.normal[1]],
        stops: [0, 100]
      }
    },
    stroke: {
      lineCap: 'round'
    },
    labels: [config.unit]
  };

  const gauge = new ApexCharts(element, options);
  gauge.render();

  return { chart: gauge, config: config };
}

// ========================================
// GAUGE INITIALIZATION
// ========================================

async function loadDashboardData() {
  try {
    const response = await fetch('/dashboard/data');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    // Update gauges with new data
    updateGauge('temp', data.dht_temperature);
    updateGauge('humidity', data.dht_humidity);
    updateGauge('pressure', data.pressure);
    updateGauge('solar', data.solar);
    updateGauge('waterPressure', data.water_pressure);
    updateGauge('ph', data.ph);
    updateGauge('ec', data.ec);

  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
}

function initializeGauges() {
  const element = document.querySelector('#historyChart');
  if (!element) return;

  const options = {
    chart: {
      type: 'line',
      height: 350,
      animations: {
        enabled: true
      },
      toolbar: {
        show: true,
        tools: {
          download: true,
          zoom: true,
          pan: true
        }
      }
    },
    series: [
      { name: 'Temperatura (°C)', data: [], color: '#ef4444' },
      { name: 'Humedad (%)', data: [], color: '#3b82f6' },
      { name: 'Presión (hPa)', data: [], color: '#8b5cf6' },
      { name: 'Solar (W/m²)', data: [], color: '#f59e0b' }
    ],
    stroke: {
      width: 3,
      curve: 'smooth'
    },
    xaxis: {
      categories: [],
      labels: {
        rotate: -45,
        style: {
          fontSize: '11px'
        }
      }
    },
    yaxis: [
      {
        title: { text: 'Temp/Hum' },
        labels: { formatter: val => val.toFixed(1) }
      },
      {
        opposite: true,
        title: { text: 'Presión/Solar' },
        labels: { formatter: val => val.toFixed(0) }
      }
    ],
    legend: {
      position: 'top',
      horizontalAlign: 'center'
    },
    grid: {
      borderColor: '#e5e7eb',
      strokeDashArray: 4
    },
    tooltip: {
      shared: true,
      intersect: false,
      y: {
        formatter: function(val, opts) {
          if (val === null || val === undefined) return 'N/A';
          return val.toFixed(1);
        }
      }
    }
  };

  historyChart = new ApexCharts(element, options);
  historyChart.render();

  console.log("✓ Chart initialized");
}

// Load historical data from server
async function loadHistoricalData() {
  try {
    const response = await fetch('/dashboard/history');
    if (!response.ok) {
      console.error('Failed to load historical data');
      return;
    }

    const data = await response.json();
    if (!data || data.length === 0) {
      console.log('No historical data available');
      return;
    }

    // Separar datos por sensor
    const tempData = [];
    const humData = [];
    const presData = [];
    const solData = [];
    const labels = [];

    data.forEach(record => {
      // Extraer la hora del timestamp
      const time = new Date(record.timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
      });
      labels.push(time);

      tempData.push(record.temperature || null);
      humData.push(record.humidity || null);
      presData.push(record.pressure || null);
      solData.push(record.solar || null);
    });

    // Actualizar el gráfico
    if (historyChart) {
      historyChart.updateOptions({
        series: [
          { name: 'Temperatura (°C)', data: tempData, color: '#ef4444' },
          { name: 'Humedad (%)', data: humData, color: '#3b82f6' },
          { name: 'Presión (hPa)', data: presData, color: '#8b5cf6' },
          { name: 'Solar (W/m²)', data: solData, color: '#f59e0b' }
        ],
        xaxis: {
          categories: labels
        }
      }, false);

      historyChart.render();
      console.log(`✓ Chart updated with ${data.length} records`);
    }

  } catch (error) {
    console.error('Error loading historical data:', error);
  }
}

// ========================================
// DATA REFRESH
// ========================================

function refresh() {
  loadDashboardData();
  loadHistoricalData();
}

async function loadDashboardData() {
  try {
    const response = await fetch('/dashboard/data');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    // Update gauges with new data
    updateGauge('temp', data.dht_temperature);
    updateGauge('humidity', data.dht_humidity);
    updateGauge('pressure', data.pressure);
    updateGauge('solar', data.solar);
    updateGauge('waterPressure', data.water_pressure);
    updateGauge('ph', data.ph);
    updateGauge('ec', data.ec);

  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
}

// ========================================
// UPDATE FUNCTIONS
// ========================================

function updateGauge(gaugeName, value) {
  const gauge = gauges[gaugeName];
  if (!gauge) return;

  const config = gauge.w.config.chart;
  const type = config.type;

  // Handle null or undefined values
  if (value === null || typeof value === 'undefined') {
    gauge.updateSeries([0]);
    // Optionally, display 'N/A' or similar
    return;
  }

  // Update daily stats
  const stats = dailyStats[type];
  if (stats) {
    if (stats.min === null || value < stats.min) stats.min = value;
    if (stats.max === null || value > stats.max) stats.max = value;

    // Update min/max display
    const minEl = document.querySelector(`#${gaugeName}Min`);
    const maxEl = document.querySelector(`#${gaugeName}Max`);
    if (minEl) minEl.textContent = `Min: ${stats.min.toFixed(1)}`;
    if (maxEl) maxEl.textContent = `Max: ${stats.max.toFixed(1)}`;
  }

  // Calculate percentage for radial bar
  const min = gauge.w.config.chart.min;
  const max = gauge.w.config.chart.max;
  const percentage = ((value - min) / (max - min)) * 100;

  gauge.updateSeries([percentage]);

  // Update color based on criticality
  const newColor = getCriticalityColor(type, value);
  gauge.updateOptions({
    colors: [newColor[0]],
    fill: {
      gradient: {
        stops: [0, 100],
        colorStops: [
          { offset: 0, color: newColor[0], opacity: 1 },
          { offset: 100, color: newColor[1], opacity: 1 }
        ]
      }
    }
  });
}

function updateTemperature(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('temperature', numValue);

  // Update gauge
  const percentage = ((numValue - 0) / (50 - 0)) * 100;
  const criticality = getCriticality('temperature', numValue);
  updateGauge('temp', percentage, criticality);

  // Update KPI
  document.getElementById('kpiTemp').textContent = `${numValue.toFixed(1)}°C`;
  updateKpiRange('temperature', numValue);
  updateStatusBadge('tempStatus', criticality);

  // Update trend
  updateTrend('tempTrend', dailyStats.temperature.values);
}

function updateHumidity(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('humidity', numValue);

  // Update gauge
  const percentage = numValue;
  const criticality = getCriticality('humidity', numValue);
  updateGauge('humidity', percentage, criticality);

  // Update KPI
  document.getElementById('kpiHum').textContent = `${numValue.toFixed(1)}%`;
  updateKpiRange('humidity', numValue);
  updateStatusBadge('humStatus', criticality);

  // Update trend
  updateTrend('humTrend', dailyStats.humidity.values);
}

function updatePressure(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('pressure', numValue);

  // Update gauge
  const percentage = ((numValue - 950) / (1050 - 950)) * 100;
  const criticality = getCriticality('pressure', numValue);
  updateGauge('pressure', percentage, criticality);

  // Update KPI
  document.getElementById('kpiPressure').textContent = `${numValue.toFixed(1)} hPa`;
  updateKpiRange('pressure', numValue);
  updateStatusBadge('pressureStatus', criticality);

  // Update trend
  updateTrend('pressureTrend', dailyStats.pressure.values);
}

function updateSolar(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('solar', numValue);

  // Update gauge
  const percentage = (numValue / 1200) * 100;
  const criticality = getCriticality('solar', numValue);
  updateGauge('solar', percentage, criticality);

  // Update KPI
  document.getElementById('kpiSolar').textContent = `${numValue.toFixed(0)} W/m²`;
  updateKpiRange('solar', numValue);
  updateStatusBadge('solarStatus', criticality);

  // Update trend
  updateTrend('solarTrend', dailyStats.solar.values);
}

// ========================================
// GAUGE UPDATE WITH COLOR CHANGE
// ========================================

function updateGauge(type, percentage, criticality) {
  const gauge = gauges[type];
  if (!gauge || !gauge.chart) return;

  // Update colors based on criticality
  const gaugeColors = colors[criticality];

  gauge.chart.updateOptions({
    colors: [gaugeColors[0]],
    fill: {
      gradient: {
        gradientToColors: [gaugeColors[1]]
      }
    }
  });

  // Update value
  gauge.chart.updateSeries([Math.min(100, Math.max(0, percentage))]);
}

// ========================================
// CRITICALITY CALCULATION
// ========================================

function getCriticality(type, value) {
  const threshold = thresholds[type];
  if (!threshold) return 'normal';

  // Temperature, Humidity, Pressure (range-based)
  if (threshold.critical && threshold.warning) {
    if (value < threshold.critical.min || value > threshold.critical.max) {
      return 'critical';
    }
    if (value < threshold.warning.min || value > threshold.warning.max) {
      return 'warning';
    }
    return 'normal';
  }

  // Solar (max-only based)
  if (type === 'solar') {
    if (value > threshold.critical.max) return 'critical';
    if (value > threshold.warning.max) return 'warning';
    return 'normal';
  }

  return 'normal';
}

// ========================================
// DAILY STATS TRACKING
// ========================================

function updateDailyStats(type, value) {
  const stats = dailyStats[type];

  // Add to values array
  stats.values.push(value);
  if (stats.values.length > 20) {
    stats.values.shift(); // Keep last 20 values
  }

  // Update min/max
  if (stats.min === null || value < stats.min) {
    stats.min = value;
  }
  if (stats.max === null || value > stats.max) {
    stats.max = value;
  }
}

function updateKpiRange(type, currentValue) {
  const stats = dailyStats[type];
  const minEl = document.getElementById(`${type}Min`);
  const maxEl = document.getElementById(`${type}Max`);

  if (minEl && stats.min !== null) {
    minEl.textContent = `Min: ${stats.min.toFixed(1)}`;
  }

  if (maxEl && stats.max !== null) {
    maxEl.textContent = `Max: ${stats.max.toFixed(1)}`;
  }
}

function updateTrend(elementId, values) {
  const element = document.getElementById(elementId);
  if (!element || values.length < 2) return;

  const recent = values.slice(-5);
  const trend = recent[recent.length - 1] - recent[0];

  if (Math.abs(trend) < 0.1) {
    element.textContent = '→';
    element.style.color = '#6b7280';
  } else if (trend > 0) {
    element.textContent = '↗';
    element.style.color = '#ef4444';
  } else {
    element.textContent = '↘';
    element.style.color = '#3b82f6';
  }
}

function updateWaterPressure(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('waterPressure', numValue);

  // Update gauge
  const percentage = ((numValue - 0) / (8 - 0)) * 100;
  const criticality = getCriticality('waterPressure', numValue);
  updateGauge('waterPressure', percentage, criticality);

  // Update status badge
  updateStatusBadge('waterPressureStatus', criticality);
}

function updatePH(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('ph', numValue);

  // Update gauge
  const percentage = ((numValue - 0) / (14 - 0)) * 100;
  const criticality = getCriticality('ph', numValue);
  updateGauge('ph', percentage, criticality);

  // Update status badge
  updateStatusBadge('phStatus', criticality);
}

function updateEC(value) {
  if (value === null || value === undefined) return;

  const numValue = Number(value);
  updateDailyStats('ec', numValue);

  // Update gauge
  const percentage = ((numValue - 0) / (4 - 0)) * 100;
  const criticality = getCriticality('ec', numValue);
  updateGauge('ec', percentage, criticality);

  // Update status badge
  updateStatusBadge('ecStatus', criticality);
}

function updateStatusBadge(elementId, criticality) {
  const element = document.getElementById(elementId);
  if (!element) return;

  element.className = 'gauge-status-badge ' + criticality;
  element.textContent = criticality.toUpperCase();
}

// ========================================
// SYSTEM STATUS
// ========================================

function updateSystemStatus() {
  const lastReading = document.getElementById('lastReading');
  if (lastReading) {
    lastReading.textContent = 'Hace 5s';
  }

  // Check overall system criticality
  const hasWarning = Object.keys(dailyStats).some(type => {
    const value = dailyStats[type].values[dailyStats[type].values.length - 1];
    return value && getCriticality(type, value) === 'warning';
  });

  const hasCritical = Object.keys(dailyStats).some(type => {
    const value = dailyStats[type].values[dailyStats[type].values.length - 1];
    return value && getCriticality(type, value) === 'critical';
  });

  const statusEl = document.getElementById('gaugeStatus');
  if (statusEl) {
    if (hasCritical) {
      statusEl.textContent = 'Crítico';
      statusEl.style.color = '#ef4444';
      showAlert('⚠️ Valores críticos detectados en sensores', 'warning');
    } else if (hasWarning) {
      statusEl.textContent = 'Alerta';
      statusEl.style.color = '#f59e0b';
    } else {
      statusEl.textContent = 'Normal';
      statusEl.style.color = '#22c55e';
    }
  }
}

// ========================================
// CHART CONTROLS
// ========================================

function toggleSensor(sensor) {
  const index = visibleSensors.indexOf(sensor);
  if (index > -1) {
    visibleSensors.splice(index, 1);
  } else {
    visibleSensors.push(sensor);
  }

  // Update button states
  const buttons = document.querySelectorAll('.chart-btn');
  buttons.forEach(btn => {
    const sensor = btn.textContent.toLowerCase().includes('temperatura') ? 'temp' :
                   btn.textContent.toLowerCase().includes('humedad') ? 'humidity' :
                   btn.textContent.toLowerCase().includes('presión') ? 'pressure' : 'solar';

    if (visibleSensors.includes(sensor)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Refresh chart would go here
}

// ========================================
// UTILITIES
// ========================================

function showAlert(message, type = 'warning') {
  const banner = document.getElementById('alertBanner');
  const messageEl = document.getElementById('alertMessage');

  if (banner && messageEl) {
    messageEl.textContent = message;
    banner.style.display = 'block';

    setTimeout(() => {
      banner.style.display = 'none';
    }, 5000);
  }
}

function closeAlert() {
  const banner = document.getElementById('alertBanner');
  if (banner) {
    banner.style.display = 'none';
  }
}

function scheduleResetDailyStats() {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);

  const timeUntilMidnight = tomorrow - now;

  setTimeout(() => {
    resetDailyStats();
    scheduleResetDailyStats(); // Schedule next reset
  }, timeUntilMidnight);
}

function resetDailyStats() {
  Object.keys(dailyStats).forEach(type => {
    dailyStats[type] = { min: null, max: null, values: [] };
  });
  console.log("📊 Daily stats reset");
}

console.log("✓ Dashboard ready");
