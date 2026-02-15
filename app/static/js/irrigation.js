const timers = {}
const intervals = {}

function formatTime(seconds){
  const m = String(Math.floor(seconds / 60)).padStart(2,"0")
  const s = String(seconds % 60).padStart(2,"0")
  return `${m}:${s}`
}

async function createSchedule(){

  const sector = document.getElementById("sector").value
  const start_time = document.getElementById("start").value

  const r = await fetch("/irrigation/schedule/add",{
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    credentials:"same-origin",
    body: JSON.stringify({
      sector,
      start_time
    })
  })

  if(!r.ok){
    alert("Error guardando")
    return
  }

  alert("Riego programado correctamente")
  location.reload()
}


//recargar tabla sin refrescar
async function loadSchedules(){
  const r = await fetch("/irrigation/schedule/list")
  const rows = await r.json()

  const table = document.querySelector("#scheduleTable tbody")
  table.innerHTML = ""

  rows.forEach(s=>{
    table.innerHTML += `
      <tr>
        <td>${s.sector}</td>
        <td>${s.date}</td>
        <td>${s.start}</td>
        <td>${s.end}</td>
      </tr>
    `
  })
}

async function toggleZone(id){
  try{
    const r = await fetch(`/irrigation/toggle/${id}`, { method:"POST" })
    if(!r.ok) return

    const card = document.getElementById(`zone-${id}`)
    const status = card.querySelector(".zone-status")
    const timerEl = document.getElementById(`timer-${id}`)

    card.classList.toggle("active")

    if(card.classList.contains("active")){
      status.textContent = "RIEGO ACTIVO"
      timers[id] = Date.now()

      intervals[id] = setInterval(()=>{
        const elapsed = Math.floor((Date.now() - timers[id]) / 1000)
        timerEl.textContent = formatTime(elapsed)
      }, 1000)

    }else{
      status.textContent = "APAGADO"
      clearInterval(intervals[id])
      timerEl.textContent = "00:00"
    }

  }catch(e){
    console.error("Toggle error:", e)
  }
}

window.toggleZone = toggleZone
