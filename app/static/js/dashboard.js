// ---------- GAUGES ----------

function gauge(el, label){
  return new ApexCharts(el,{
    chart:{ type:"radialBar", height:240 },
    series:[0],
    labels:[label],
    plotOptions:{
      radialBar:{
        hollow:{ size:"70%" },
        dataLabels:{
          value:{ fontSize:"26px" }
        }
      }
    }
  })
}


const tempGauge = gauge(document.querySelector("#tempGauge"), "°C")
const humGauge  = gauge(document.querySelector("#humGauge"), "%")
const solGauge  = gauge(document.querySelector("#solarGauge"), "W/m²")

tempGauge.render()
humGauge.render()
solGauge.render()

// ---------- HISTORY ----------
const historyChart = new ApexCharts(
  document.querySelector("#historyChart"), {
    chart:{ type:"line", height:300 },
    series:[
      { name:"Temp", data:[] },
      { name:"Hum", data:[] }
    ],
    xaxis:{ categories:[] }
})
historyChart.render()

// ---------- AJAX ----------
async function refresh(){
  const r = await fetch("/dashboard/data")
  const d = await r.json()

  tempGauge.updateSeries([d.temperature])
  humGauge.updateSeries([d.humidity])
  solGauge.updateSeries([d.solar])

  document.getElementById("kpiTemp").innerText = d.temperature
  document.getElementById("kpiHum").innerText = d.humidity
  document.getElementById("kpiSolar").innerText = d.solar
  document.getElementById("kpiWater").innerText = d.water_liters.toFixed(1)

  document.getElementById("datetime").innerText =
    new Date(d.time).toLocaleString()

}

refresh()
setInterval(refresh, 5000)
