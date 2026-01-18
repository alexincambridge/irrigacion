// ---------- GAUGE FACTORY ----------

function createGauge(selector, unit, max){
  const chart = new ApexCharts(
    document.querySelector(selector),
    {
      chart:{ type:"radialBar", height:200 },
      series:[0],
      labels:[unit],
      plotOptions:{
        radialBar:{
          hollow:{ size:"60%" },
          dataLabels:{
            value:{ fontSize:"24px" }
          }
        }
      },
      yaxis:{ max:max }
    }
  )
  chart.render()
  return chart
}

// ---------- GAUGES ----------

const tempGauge     = createGauge("#tempGauge", "°C", 50)
const humGauge      = createGauge("#humGauge", "%", 100)
const solarGauge    = createGauge("#solarGauge", "W/m²", 1200)
const pressureGauge = createGauge("#pressureGauge", "hPa", 1100)
const ecGauge       = createGauge("#ecGauge", "mS/cm", 5)
const phGauge       = createGauge("#phGauge", "pH", 14)

// ---------- HISTORY CHART ----------

const historyChart = new ApexCharts(
  document.querySelector("#historyChart"),
  {
    chart:{ type:"line", height:300 },
    series:[
      { name:"Temperatura", data:[] },
      { name:"Humedad", data:[] }
    ],
    xaxis:{ categories:[] }
  }
)
historyChart.render()

// ---------- AJAX FUNCTIONS ----------

async function updateLatest(){
  try{
    const r = await fetch("/latest")
    const d = await r.json()
    if(!d || d.temperature === null) return

    tempGauge.updateSeries([d.temperature])
    humGauge.updateSeries([d.humidity])
    solarGauge.updateSeries([d.solar])
    pressureGauge.updateSeries([d.pressure])
    ecGauge.updateSeries([d.ec])
    phGauge.updateSeries([d.ph])

  }catch(e){
    console.error("Latest error", e)
  }
}

async function updateHistory(){
  try{
    const r = await fetch("/history")
    const rows = await r.json()

    historyChart.updateOptions({
      series:[
        { name:"Temperatura", data: rows.map(r=>r.temperature) },
        { name:"Humedad", data: rows.map(r=>r.humidity) }
      ],
      xaxis:{
        categories: rows.map(r=>r.time)
      }
    })
  }catch(e){
    console.error("History error", e)
  }
}

// ---------- INTERVALS ----------

// Real-time (sensación live)
updateLatest()
setInterval(updateLatest, 3000)

// Histórico
updateHistory()
setInterval(updateHistory, 60000)


