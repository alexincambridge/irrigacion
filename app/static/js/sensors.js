const sensorChart = new ApexCharts(
  document.querySelector("#sensorChart"),
  {
    chart:{ type:"line", height:400 },
    series:[
      { name:"Temp °C", data:[] },
      { name:"Hum %", data:[] },
      { name:"Solar", data:[] },
      { name:"Presión", data:[] },
      { name:"EC", data:[] },
      { name:"pH", data:[] }
    ],
    xaxis:{ categories:[] }
  }
)

sensorChart.render()

async function loadHistory(){
  const r = await fetch("/history")
  const rows = await r.json()

  sensorChart.updateOptions({
    series:[
      { name:"Temp °C", data: rows.map(r=>r.temperature) },
      { name:"Hum %", data: rows.map(r=>r.humidity) },
      { name:"Solar", data: rows.map(r=>r.solar) },
      { name:"Presión", data: rows.map(r=>r.pressure) },
      { name:"EC", data: rows.map(r=>r.ec) },
      { name:"pH", data: rows.map(r=>r.ph) }
    ],
    xaxis:{
      categories: rows.map(r=>r.timestamp)
    }
  })
}

loadHistory()
