// ========================================
// INDUSTRIAL DASHBOARD - PROFESSIONAL JS
// Dynamic gauges with criticality colors
// ========================================

console.log("🏭 Industrial Dashboard initialized");

// State management
let dailyStats = {
  temperature: { min: null, max: null },
  humidity: { min: null, max: null },
  pressure: { min: null, max: null },
  solar: { min: null, max: null },
  waterPressure: { min: null, max: null },
  ph: { min: null, max: null },
  ec: { min: null, max: null }
};

let gauges = {};
let historyChart = null;
let visibleSensors = ['temp', 'humidity', 'pressure', 'solar'];

// Criticality thresholds
const thresholds = {
  temperature: { critical: { min: 5, max: 40 }, warning: { min: 10, max: 35 }, normal: { min: 15, max: 30 } },
  humidity:    { critical: { min: 20, max: 90 }, warning: { min: 30, max: 80 }, normal: { min: 40, max: 70 } },
  pressure:    { critical: { min: 980, max: 1040 }, warning: { min: 990, max: 1030 }, normal: { min: 1000, max: 1020 } },
  solar:       { critical: { max: 1000 }, warning: { max: 800 } },
  waterPressure: { critical: { min: 0.5, max: 6 }, warning: { min: 1, max: 5 }, normal: { min: 1.5, max: 4 } },
  ph:          { critical: { min: 5.5, max: 8.5 }, warning: { min: 6, max: 8 }, normal: { min: 6.5, max: 7.5 } },
  ec:          { critical: { min: 0.5, max: 2.5 }, warning: { min: 0.8, max: 2 }, normal: { min: 1, max: 1.8 } }
};

// Color schemes for criticality
const colors = {
  normal: ['#22c55e', '#16a34a'],
  warning: ['#f59e0b', '#d97706'],
  critical: ['#ef4444', '#dc2626']
};

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  initializeGauges();
  initializeChart();
  loadDashboardData();
  loadHistoricalData();
  setInterval(function() {
    loadDashboardData();
    loadHistoricalData();
  }, 10000);
  scheduleResetDailyStats();
});

// ========================================
// GAUGE CREATION
// ========================================

function initializeGauges() {
  gauges.temp = createGauge('tempGauge', { min: 0, max: 50, unit: '°C', type: 'temperature', height: 120 });
  gauges.humidity = createGauge('humGauge', { min: 0, max: 100, unit: '%', type: 'humidity', height: 120 });
  gauges.pressure = createGauge('pressureGauge', { min: 950, max: 1050, unit: 'hPa', type: 'pressure', height: 120 });
  gauges.solar = createGauge('solarGauge', { min: 0, max: 1200, unit: 'W/m²', type: 'solar', height: 120 });
  gauges.waterPressure = createGauge('waterPressureGauge', { min: 0, max: 8, unit: 'bar', type: 'waterPressure', height: 120 });
  gauges.ph = createGauge('phGauge', { min: 0, max: 14, unit: 'pH', type: 'ph', height: 120 });
  gauges.ec = createGauge('ecGauge', { min: 0, max: 4, unit: 'mS', type: 'ec', height: 120 });
  console.log("✓ Gauges initialized");
}

function createGauge(elementId, config) {
  var element = document.getElementById(elementId);
  if (!element) {
    console.warn("Gauge element not found: #" + elementId);
    return null;
  }
  // Ensure container has dimensions so ApexCharts doesn't complain
  if (!element.style.minHeight) {
    element.style.minHeight = (config.height || 120) + 'px';
  }

  var options = {
    chart: {
      type: 'radialBar',
      height: config.height || 280,
      animations: { enabled: true, easing: 'easeinout', speed: 800 }
    },
    series: [0],
    colors: [colors.normal[0]],
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 135,
        hollow: { size: '65%', background: 'transparent' },
        track: { background: '#f1f5f9', strokeWidth: '100%', margin: 5 },
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
              var actual = (val / 100) * (config.max - config.min) + config.min;
              return actual.toFixed(1);
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
    stroke: { lineCap: 'round' },
    labels: [config.unit]
  };

  var chart = new ApexCharts(element, options);
  chart.render();
  return { chart: chart, config: config };
}

// ========================================
// DATA LOADING
// ========================================

async function loadDashboardData() {
  try {
    var response = await fetch('/dashboard/data');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    var data = await response.json();

    updateGauge('temp', data.dht_temperature, 'temperature');
    updateGauge('humidity', data.dht_humidity, 'humidity');
    updateGauge('pressure', data.pressure, 'pressure');
    updateGauge('solar', data.solar, 'solar');
    updateGauge('waterPressure', data.water_pressure, 'waterPressure');
    updateGauge('ph', data.ph, 'ph');
    updateGauge('ec', data.ec, 'ec');

  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
}

// ========================================
// GAUGE UPDATE + KPI INDICATORS
// ========================================

// Map gauge names to HTML element IDs
var gaugeMap = {
  temp:          { kpi: 'kpiTemp',          unit: '°C',   kpiMin: 'kpiTempMin',          kpiMax: 'kpiTempMax',          gaugeMin: 'tempMin',          gaugeMax: 'tempMax',          badge: 'tempStatus',          trend: 'tempTrend' },
  humidity:      { kpi: 'kpiHum',           unit: '%',    kpiMin: 'kpiHumMin',           kpiMax: 'kpiHumMax',           gaugeMin: 'humidityMin',      gaugeMax: 'humidityMax',      badge: 'humStatus',           trend: 'humTrend' },
  pressure:      { kpi: 'kpiPressure',      unit: ' hPa', kpiMin: 'kpiPressureMin',      kpiMax: 'kpiPressureMax',      gaugeMin: 'pressureMin',      gaugeMax: 'pressureMax',      badge: 'pressureStatus',      trend: 'pressureTrend' },
  solar:         { kpi: 'kpiSolar',         unit: ' W/m²',kpiMin: 'kpiSolarMin',         kpiMax: 'kpiSolarMax',         gaugeMin: 'solarMin',         gaugeMax: 'solarMax',         badge: 'solarStatus',         trend: 'solarTrend' },
  waterPressure: { kpi: null,               unit: ' bar', kpiMin: null,                  kpiMax: null,                  gaugeMin: 'waterPressureMin', gaugeMax: 'waterPressureMax', badge: 'waterPressureStatus', trend: null },
  ph:            { kpi: null,               unit: '',     kpiMin: null,                  kpiMax: null,                  gaugeMin: 'phMin',            gaugeMax: 'phMax',            badge: 'phStatus',            trend: null },
  ec:            { kpi: null,               unit: ' mS',  kpiMin: null,                  kpiMax: null,                  gaugeMin: 'ecMin',            gaugeMax: 'ecMax',            badge: 'ecStatus',            trend: null }
};

function updateGauge(gaugeName, value, type) {
  var gaugeObj = gauges[gaugeName];
  if (!gaugeObj || !gaugeObj.chart) return;

  var config = gaugeObj.config;
  var map = gaugeMap[gaugeName];

  // Handle null/undefined
  if (value === null || typeof value === 'undefined') {
    gaugeObj.chart.updateSeries([0]);
    return;
  }

  var numValue = Number(value);
  var decimals = (type === 'solar') ? 0 : 1;

  // --- 1. Update daily min/max stats ---
  var stats = dailyStats[type];
  if (stats) {
    if (stats.min === null || numValue < stats.min) stats.min = numValue;
    if (stats.max === null || numValue > stats.max) stats.max = numValue;
  }

  // --- 2. Update KPI text value (e.g. "23.5°C") ---
  if (map && map.kpi) {
    var kpiEl = document.getElementById(map.kpi);
    if (kpiEl) kpiEl.textContent = numValue.toFixed(decimals) + map.unit;
  }

  // --- 3. Update KPI min/max ---
  if (map && stats) {
    if (map.kpiMin) {
      var kpiMinEl = document.getElementById(map.kpiMin);
      if (kpiMinEl) kpiMinEl.textContent = 'Min: ' + stats.min.toFixed(decimals);
    }
    if (map.kpiMax) {
      var kpiMaxEl = document.getElementById(map.kpiMax);
      if (kpiMaxEl) kpiMaxEl.textContent = 'Max: ' + stats.max.toFixed(decimals);
    }
  }

  // --- 4. Update Gauge min/max ---
  if (map && stats) {
    if (map.gaugeMin) {
      var gMinEl = document.getElementById(map.gaugeMin);
      if (gMinEl) gMinEl.textContent = 'Min: ' + stats.min.toFixed(decimals);
    }
    if (map.gaugeMax) {
      var gMaxEl = document.getElementById(map.gaugeMax);
      if (gMaxEl) gMaxEl.textContent = 'Max: ' + stats.max.toFixed(decimals);
    }
  }

  // --- 5. Update gauge radial bar ---
  var percentage = ((numValue - config.min) / (config.max - config.min)) * 100;
  percentage = Math.min(100, Math.max(0, percentage));
  gaugeObj.chart.updateSeries([percentage]);

  // --- 6. Update gauge color based on criticality ---
  var crit = getCriticality(type, numValue);
  var gaugeColors = colors[crit] || colors.normal;
  gaugeObj.chart.updateOptions({
    colors: [gaugeColors[0]],
    fill: { gradient: { gradientToColors: [gaugeColors[1]] } }
  });

  // --- 7. Update status badge ---
  if (map && map.badge) {
    var badge = document.getElementById(map.badge);
    if (badge) {
      badge.className = 'gauge-status-badge ' + crit;
      badge.textContent = crit === 'critical' ? 'CRÍTICO' : crit === 'warning' ? 'ALERTA' : 'NORMAL';
    }
  }

  // --- 8. Update trend arrow ---
  if (map && map.trend) {
    var trendEl = document.getElementById(map.trend);
    if (trendEl && stats && stats.prev !== undefined) {
      if (numValue > stats.prev) {
        trendEl.textContent = '↗'; trendEl.style.color = '#ef4444';
      } else if (numValue < stats.prev) {
        trendEl.textContent = '↘'; trendEl.style.color = '#3b82f6';
      } else {
        trendEl.textContent = '→'; trendEl.style.color = '#6b7280';
      }
    }
    if (stats) stats.prev = numValue;
  }

  // --- 9. Update indicator timestamp ---
  var indicator = document.getElementById('updateIndicator');
  if (indicator) {
    var now = new Date().toLocaleTimeString('es-ES');
    indicator.innerHTML = '<span class="pulse-dot"></span> ' + now;
  }
}

// ========================================
// CRITICALITY
// ========================================

function getCriticality(type, value) {
  var t = thresholds[type];
  if (!t) return 'normal';

  if (t.critical) {
    if ((t.critical.min !== undefined && value < t.critical.min) ||
        (t.critical.max !== undefined && value > t.critical.max)) {
      return 'critical';
    }
  }
  if (t.warning) {
    if ((t.warning.min !== undefined && value < t.warning.min) ||
        (t.warning.max !== undefined && value > t.warning.max)) {
      return 'warning';
    }
  }
  return 'normal';
}

function getCriticalityColor(type, value) {
  return colors[getCriticality(type, value)] || colors.normal;
}

// ========================================
// HISTORICAL CHART
// ========================================

function initializeChart() {
  var element = document.querySelector('#historyChart');
  if (!element) return;

  var options = {
    chart: {
      type: 'line',
      height: 350,
      animations: { enabled: true },
      toolbar: { show: true, tools: { download: true, zoom: true, pan: true } }
    },
    series: [
      { name: 'Temperatura (°C)', data: [] },
      { name: 'Humedad (%)', data: [] },
      { name: 'Presión (hPa)', data: [] },
      { name: 'Solar (W/m²)', data: [] }
    ],
    colors: ['#ef4444', '#3b82f6', '#8b5cf6', '#f59e0b'],
    stroke: { width: [3, 3, 2, 2], curve: 'smooth' },
    xaxis: {
      categories: [],
      labels: { rotate: -45, style: { fontSize: '11px' } }
    },
    yaxis: [
      {
        seriesName: 'Temperatura (°C)',
        title: { text: 'Temp (°C) / Hum (%)' },
        labels: { formatter: function(v) { return v !== null && v !== undefined ? v.toFixed(1) : ''; } },
        min: 0, max: 100
      },
      {
        seriesName: 'Humedad (%)',
        show: false,
        min: 0, max: 100
      },
      {
        opposite: true,
        seriesName: 'Presión (hPa)',
        title: { text: 'Presión (hPa)' },
        labels: { formatter: function(v) { return v !== null && v !== undefined ? v.toFixed(0) : ''; } }
      },
      {
        opposite: true,
        seriesName: 'Solar (W/m²)',
        show: false
      }
    ],
    legend: { position: 'top', horizontalAlign: 'center' },
    grid: { borderColor: '#e5e7eb', strokeDashArray: 4 },
    tooltip: {
      shared: true, intersect: false,
      y: { formatter: function(v) { return (v === null || v === undefined) ? 'N/A' : v.toFixed(1); } }
    }
  };

  historyChart = new ApexCharts(element, options);
  historyChart.render();
  console.log("✓ Chart initialized");
}

async function loadHistoricalData() {
  try {
    var response = await fetch('/dashboard/history');
    if (!response.ok) return;
    var data = await response.json();
    if (!data || data.error || !Array.isArray(data) || data.length === 0) {
      console.log("📊 No historical data available yet (records: " + (data ? data.length : 0) + ")");
      return;
    }
    console.log("📊 Historical data loaded: " + data.length + " records");

    var labels = [], tempData = [], humData = [], presData = [], solData = [];

    data.forEach(function(record) {
      // Handle SQLite datetime format "YYYY-MM-DD HH:MM:SS" by replacing space with T
      var ts = record.timestamp || '';
      if (ts.indexOf('T') === -1 && ts.indexOf(' ') > -1) {
        ts = ts.replace(' ', 'T');
      }
      var dateObj = new Date(ts);
      var time = isNaN(dateObj.getTime()) ? ts.slice(11, 16) : dateObj.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
      labels.push(time);
      tempData.push(record.temperature !== null && record.temperature !== undefined ? record.temperature : null);
      humData.push(record.humidity !== null && record.humidity !== undefined ? record.humidity : null);
      presData.push(record.pressure !== null && record.pressure !== undefined ? record.pressure : null);
      solData.push(record.solar !== null && record.solar !== undefined ? record.solar : null);
    });

    if (historyChart) {
      historyChart.updateOptions({
        series: [
          { name: 'Temperatura (°C)', data: tempData },
          { name: 'Humedad (%)', data: humData },
          { name: 'Presión (hPa)', data: presData },
          { name: 'Solar (W/m²)', data: solData }
        ],
        xaxis: { categories: labels }
      }, true, true);
    }
  } catch (error) {
    console.error('Error loading historical data:', error);
  }
}

// ========================================
// CHART CONTROLS
// ========================================

function toggleSensor(sensor) {
  var index = visibleSensors.indexOf(sensor);
  if (index > -1) {
    visibleSensors.splice(index, 1);
  } else {
    visibleSensors.push(sensor);
  }
}

// ========================================
// UTILITIES
// ========================================

function showAlert(message, type) {
  var banner = document.getElementById('alertBanner');
  var messageEl = document.getElementById('alertMessage');
  if (banner && messageEl) {
    messageEl.textContent = message;
    banner.style.display = 'block';
    setTimeout(function() { banner.style.display = 'none'; }, 5000);
  }
}

function closeAlert() {
  var banner = document.getElementById('alertBanner');
  if (banner) banner.style.display = 'none';
}

function scheduleResetDailyStats() {
  var now = new Date();
  var tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);
  var ms = tomorrow - now;
  setTimeout(function() {
    resetDailyStats();
    scheduleResetDailyStats();
  }, ms);
}

function resetDailyStats() {
  Object.keys(dailyStats).forEach(function(type) {
    dailyStats[type] = { min: null, max: null };
  });
  console.log("📊 Daily stats reset");
}

console.log("✓ Dashboard ready");
