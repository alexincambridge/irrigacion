setInterval(()=>{
 fetch('/data').then(r=>r.json()).then(d=>{
   document.getElementById("temp").innerText=d.temperature+" °C"
   document.getElementById("hum").innerText=d.humidity+" %"
 })
},3000)
