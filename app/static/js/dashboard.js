function gaugeColor(v, ranges){
  if(v < ranges.warn[0] || v > ranges.warn[1]) return "#ef4444"
  if(v < ranges.ok[0]   || v > ranges.ok[1])   return "#facc15"
  return "#22c55e"
}

function createGauge(el, max, unit, ranges){
  const chart = new ApexCharts(
    document.querySelector(el),
    {
      chart:{ type:"radialBar", height:220 },
      series:[0],
      colors:["#22c55e"],
      plotOptions:{
        radialBar:{
          hollow:{ size:"65%" },
          dataLabels:{
            value:{
              formatter:(v)=> v + " " + unit,
              fontSize:"22px"
            }
          }
        }
      },
      yaxis:{ max:max }
    }
  )
  chart.render()
  chart._ranges = ranges
  return chart
}


// Crear gauges
//const gTemp     = createGauge("#g_temp", 50, "°C")
//const gHum      = createGauge("#g_hum", 100, "%")
//const gSolar    = createGauge("#g_solar", 1200, "W/m²")
//const gPressure = createGauge("#g_pressure", 1100, "hPa")
//const gEC       = createGauge("#g_ec", 5, "mS")
//const gPH       = createGauge("#g_ph", 14, "")

const gTemp = createGauge("#g_temp", 50, "°C", {
  ok:[18,28], warn:[15,35]
})

const gHum = createGauge("#g_hum", 100, "%", {
  ok:[40,70], warn:[30,85]
})

const gSolar = createGauge("#g_solar", 1200, "W/m²", {
  ok:[0,800], warn:[0,1000]
})

const gPressure = createGauge("#g_pressure", 1100, "hPa", {
  ok:[990,1025], warn:[970,1050]
})

const gEC = createGauge("#g_ec", 5, "mS", {
  ok:[1,2.5], warn:[0.8,3.5]
})

const gPH = createGauge("#g_ph", 14, "", {
  ok:[6,7], warn:[5.5,7.5]
})

async function updateGauges(){
  try{
    const r = await fetch("/latest")
    const d = await r.json()
    if(!d.temperature) return

    const map = [
      [gTemp, d.temperature],
      [gHum, d.humidity],
      [gSolar, d.solar],
      [gPressure, d.pressure],
      [gEC, d.ec],
      [gPH, d.ph]
    ]

    map.forEach(([g, v])=>{
      const c = gaugeColor(v, g._ranges)
      g.updateOptions({ colors:[c] })
      g.updateSeries([v])
    })

  }catch(e){
    console.error("Gauge update error", e)
  }
}


updateGauges()
setInterval(updateGauges, 3000)
