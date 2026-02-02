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

async function loadHistory(){
  const r = await fetch("/irrigation/history/data")
  const data = await r.json()

  chart.updateOptions({
    series: [{
      data: data.map(d => d.duration)
    }],
    xaxis: {
      categories: data.map(d => d.time)
    }
  })
}

loadHistory()
