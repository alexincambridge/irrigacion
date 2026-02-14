const timers = {}
const intervals = {}

function formatTime(seconds){
  const m = String(Math.floor(seconds / 60)).padStart(2,"0")
  const s = String(seconds % 60).padStart(2,"0")
  return `${m}:${s}`
}

document.addEventListener("DOMContentLoaded", function(){

  const calendarEl = document.getElementById("calendar")

  if(!calendarEl) return

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    selectable: true,

    dateClick: function(info){
      selectedDate = info.dateStr
      alert("Fecha seleccionada: " + selectedDate)
    },

    events: async function(fetchInfo, successCallback){
      const r = await fetch("/irrigation/schedule/list")
      const data = await r.json()

      const events = data.map(s => ({
  title: "Sector " + s.sector,
  start: s.date + "T" + s.start,
  end: s.date + "T" + s.end,
  color: s.sector == 1 ? "#2ecc71" :
         s.sector == 2 ? "#3498db" :
                         "#e67e22"
}))


      successCallback(events)
    }
  })

  calendar.render()

  window._calendar = calendar
})

let selectedDate = null

async function createSchedule(){

  if(!selectedDate){
    alert("Selecciona una fecha en el calendario")
    return
  }

  const sector = document.getElementById("sector").value
  const start  = document.getElementById("start").value
  const end    = document.getElementById("end").value

  const r = await fetch("/irrigation/schedule/add",{
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({
      sector: sector,
      date: selectedDate,
      start: start,
      end: end
    })
  })

  const data = await r.json()

  if(data.error){
    alert(data.error)
    return
  }

  window._calendar.refetchEvents()
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
