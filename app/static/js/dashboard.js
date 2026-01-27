alert("dashboard.js cargado");


function createGauge(el, max){
  const chart = new ApexCharts(
    document.querySelector(el),
    {
      chart:{ type:"radialBar", height:220 },
      series:[0],
      plotOptions:{
        radialBar:{
          hollow:{ size:"65%" },
          dataLabels:{ value:{ fontSize:"22px" } }
        }
      },
      yaxis:{ max:max }
    }
  )
  chart.render()
  return chart
}

// Gauges
const tempGauge     = createGauge("#tempGauge", 50)
const humGauge      = createGauge("#humGauge", 100)
const solarGauge    = createGauge("#solarGauge", 1200)
const pressureGauge = createGauge("#pressureGauge", 1100)
const ecGauge       = createGauge("#ecGauge", 5)
const phGauge       = createGauge("#phGauge", 14)

// History
const historyChart = new ApexCharts(
  document.querySelector("#historyChart"),
  {
    chart:{ type:"line", height:300 },
    series:[
      { name:"Temp", data:[] },
      { name:"Hum", data:[] }
    ],
    xaxis:{ categories:[] }
  }
)
historyChart.render()

async function updateLatest(){
  const r = await fetch("/latest")
  const d = await r.json()
  if(!d.temperature) return

  tempGauge.updateSeries([d.temperature])
  humGauge.updateSeries([d.humidity])
  solarGauge.updateSeries([d.solar])
  pressureGauge.updateSeries([d.pressure])
  ecGauge.updateSeries([d.ec])
  phGauge.updateSeries([d.ph])
}

async function updateHistory(){
  const r = await fetch("/history")
  const rows = await r.json()

  historyChart.updateOptions({
    series:[
      { name:"Temp", data: rows.map(r=>r.temperature) },
      { name:"Hum", data: rows.map(r=>r.humidity) }
    ],
    xaxis:{
      categories: rows.map(r=>r.timestamp)
    }
  })
}

updateLatest()
updateHistory()
setInterval(updateLatest, 3000)
setInterval(updateHistory, 60000)
