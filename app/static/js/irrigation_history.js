const chart = new ApexCharts(
  document.querySelector("#irrigationChart"),
  {
    chart: {
      type: "bar",
      height: 300
    },
    series: [{
      name: "Duración (min)",
      data: []
    }],
    xaxis: {
      categories: []
    }
  }
)

chart.render()

async function loadIrrigationHistory(){
  const r = await fetch("/irrigation/history/data")
  const rows = await r.json()

  chart.updateOptions({
    series: [{
      data: rows.map(r => r.duration)
    }],
    xaxis: {
      categories: rows.map(r => r.time)
    }
  })
}

loadIrrigationHistory()
