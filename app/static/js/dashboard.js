// ---------- GAUGES ----------

const tempGauge = new ApexCharts(
  document.querySelector("#tempGauge"),
  {
    chart:{ type:"radialBar", height:250 },
    series:[0],
    labels:["°C"],
    plotOptions:{
      radialBar:{
        hollow:{ size:"65%" },
        dataLabels:{ value:{ fontSize:"28px" } }
      }
    }
  }
)

const humGauge = new ApexCharts(
  document.querySelector("#humGauge"),
  {
    chart:{ type:"radialBar", height:250 },
    series:[0],
    labels:["%"],
    plotOptions:{
      radialBar:{
        hollow:{ size:"65%" },
        dataLabels:{ value:{ fontSize:"28px" } }
      }
    }
  }
)

tempGauge.render()
humGauge.render()

// ---------- HISTORY CHART ----------

const historyChart = new ApexCharts(
  document.querySelector("#historyChart"),
  {
    chart:{ type:"line", height:300, animations:{ enabled:true }},
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
    if(!d.temperature) return

    tempGauge.updateSeries([d.temperature])
    humGauge.updateSeries([d.humidity])
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

// Real-time gauges
updateLatest()
setInterval(updateLatest, 3000)   // ⏱️ 3 segundos

// Histórico
updateHistory()
setInterval(updateHistory, 60000) // ⏱️ 1 minuto
