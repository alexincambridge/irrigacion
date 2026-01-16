// ===== GAUGES =====
const tempGauge = new ApexCharts(document.querySelector("#tempGauge"), {
  chart: { type: 'radialBar', height: 220 },
  series: [0],
  labels: ['Temperatura °C'],
  plotOptions: {
    radialBar: {
      startAngle: -135,
      endAngle: 135,
      dataLabels: {
        value: { fontSize: '24px' }
      }
    }
  }
})

const humGauge = new ApexCharts(document.querySelector("#humGauge"), {
  chart: { type: 'radialBar', height: 220 },
  series: [0],
  labels: ['Humedad %'],
  plotOptions: {
    radialBar: {
      startAngle: -135,
      endAngle: 135,
      dataLabels: {
        value: { fontSize: '24px' }
      }
    }
  }
})

tempGauge.render()
humGauge.render()

// ===== LINE CHARTS =====
const tempChart = new Chart(document.getElementById("tempChart"), {
  type: 'line',
  data: { labels: [], datasets: [{ label: '°C', data: [], tension: 0.4 }] }
})

const humChart = new Chart(document.getElementById("humChart"), {
  type: 'line',
  data: { labels: [], datasets: [{ label: '%', data: [], tension: 0.4 }] }
})

function updateDashboard() {
  fetch('/history')
    .then(r => r.json())
    .then(data => {
      if (!data.length) return

      const last = data[data.length - 1]

      tempGauge.updateSeries([last.temperature])
      humGauge.updateSeries([last.humidity])

      tempChart.data.labels = data.map(d => d.time)
      tempChart.data.datasets[0].data = data.map(d => d.temperature)

      humChart.data.labels = data.map(d => d.time)
      humChart.data.datasets[0].data = data.map(d => d.humidity)

      tempChart.update()
      humChart.update()
    })
}

setInterval(updateDashboard, 5000)
updateDashboard()
