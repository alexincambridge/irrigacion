const waterChart = new ApexCharts(
  document.querySelector("#waterChart"),
  {
    chart:{ type:"area", height:300 },
    series:[{ name:"Litros", data:[] }],
    xaxis:{ categories:[] }
  }
)

waterChart.render()

async function loadWater(){
  const r = await fetch("/water/data")
  const rows = await r.json()

  waterChart.updateOptions({
    series:[{
      data: rows.map(r => r.liters)
    }],
    xaxis:{
      categories: rows.map(r => r.time)
    }
  })
}

loadWater()
