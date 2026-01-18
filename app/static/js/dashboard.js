const tempGauge = new ApexCharts(
  document.querySelector("#tempGauge"),
  {
    chart:{ type:"radialBar", height:250 },
    series:[0],
    labels:["°C"],
    plotOptions:{
      radialBar:{
        hollow:{ size:"65%" },
        dataLabels:{
          value:{ fontSize:"28px" }
        }
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
        dataLabels:{
          value:{ fontSize:"28px" }
        }
      }
    }
  }
)

tempGauge.render()
humGauge.render()

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

function updateData(){
  fetch("/latest")
    .then(r=>r.json())
    .then(d=>{
      if(!d.temperature) return
      tempGauge.updateSeries([d.temperature])
      humGauge.updateSeries([d.humidity])
    })

  fetch("/history")
    .then(r=>r.json())
    .then(rows=>{
      historyChart.updateOptions({
        series:[
          { name:"Temperatura", data: rows.map(r=>r.temperature) },
          { name:"Humedad", data: rows.map(r=>r.humidity) }
        ],
        xaxis:{
          categories: rows.map(r=>r.time)
        }
      })
    })
}

updateData()
setInterval(updateData, 60000)
