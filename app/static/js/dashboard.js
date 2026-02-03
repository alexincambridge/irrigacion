console.log("dashboard.js cargado")

function gauge(el, label){
  if(!el) return null
  return new ApexCharts(el,{
    chart:{ type:"radialBar", height:240 },
    series:[0],
    labels:[label],
    plotOptions:{
      radialBar:{
        hollow:{ size:"70%" },
        dataLabels:{ value:{ fontSize:"26px" } }
      }
    }
  })
}

// ---------- INIT ----------
const tempGauge = gauge(document.querySelector("#tempGauge"), "°C")
const humGauge  = gauge(document.querySelector("#humGauge"), "%")
const solGauge  = gauge(document.querySelector("#solarGauge"), "W/m²")

tempGauge && tempGauge.render()
humGauge  && humGauge.render()
solGauge  && solGauge.render()

const historyEl = document.querySelector("#historyChart")
const historyChart = historyEl
  ? new ApexCharts(historyEl,{
      chart:{ type:"line", height:300 },
      series:[
        { name:"Temp", data:[] },
        { name:"Hum", data:[] }
      ],
      xaxis:{ categories:[] }
    })
  : null

historyChart && historyChart.render()

// ---------- DATA ----------
async function refresh(){
  try{
    const r = await fetch("/dashboard/data")
    if(!r.ok) return

    const d = await r.json()

    if(tempGauge && d.dht_temperature != null)
      tempGauge.updateSeries([Number(d.dht_temperature)])

    if(humGauge && d.dht_humidity != null)
      humGauge.updateSeries([Number(d.dht_humidity)])

    if(solGauge && d.solar != null)
      solGauge.updateSeries([d.solar])

    const set = (id, val) => {
      const el = document.getElementById(id)
      if(el && val != null) el.innerText = val
    }

    set("kpiTemp", d.temperature)
    set("kpiHum", d.humidity)
    set("kpiSolar", d.solar)

    if(d.water_liters != null)
      set("kpiWater", d.water_liters.toFixed(1))

  }catch(e){
    console.error("Dashboard refresh error", e)
  }
}

// ---------- LOOP ----------
refresh()
setInterval(refresh, 5000)
