const tempCtx = document.getElementById("tempChart")
const humCtx = document.getElementById("humChart")

const tempChart = new Chart(tempCtx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: '°C', data: [], tension: 0.4 }] }
})

const humChart = new Chart(humCtx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: '%', data: [], tension: 0.4 }] }
})

function updateCharts(){
  fetch('/history')
    .then(r => r.json())
    .then(data => {
      tempChart.data.labels = data.map(d => d.time)
      tempChart.data.datasets[0].data = data.map(d => d.temperature)

      humChart.data.labels = data.map(d => d.time)
      humChart.data.datasets[0].data = data.map(d => d.humidity)

      tempChart.update()
      humChart.update()
    })
}

setInterval(updateCharts, 5000)
updateCharts()
