const timers = {}
const intervals = {}

function formatTime(seconds){
  const m = String(Math.floor(seconds / 60)).padStart(2,"0")
  const s = String(seconds % 60).padStart(2,"0")
  return `${m}:${s}`
}

async function createSchedule(){
  const sector = document.getElementById("sector").value
  const date   = document.getElementById("date").value
  const start  = document.getElementById("start").value
  const end    = document.getElementById("end").value

  const r = await fetch("/irrigation/schedule/add",{
  method:"POST",
  credentials:"same-origin",
  headers:{ "Content-Type":"application/json" },
  body: JSON.stringify({
    sector,
    date: selectedDate,
    start,
    end
  })
})

  if(!r.ok){
  const text = await r.text()
  console.error("Server error:", text)
  alert("Error servidor, mira consola")
  return
}


  const data = await r.json()

  if(data.error){
    alert(data.error)
    return
  }

  loadSchedules()
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
        <td>${s.duration} min</td>
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
