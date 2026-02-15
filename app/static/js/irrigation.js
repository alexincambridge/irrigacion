const timers = {}
const intervals = {}

// ---------- UTIL ----------
function formatTime(seconds){
  const m = String(Math.floor(seconds / 60)).padStart(2,"0")
  const s = String(seconds % 60).padStart(2,"0")
  return `${m}:${s}`
}

// ---------- ZONAS / RIEGO MANUAL ----------
async function toggleZone(id){
  // Alterna manualmente: start / stop
  const action = document.getElementById(`zone-${id}`).classList.contains("active") ? "stop" : "start"

  const r = await fetch("/irrigation/manual", {
    method:"POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sector: id, action })
  })
  if(!r.ok) return
  const data = await r.json()
  if(!data.success) return

  const card = document.getElementById(`zone-${id}`)
  const status = card.querySelector(".zone-status")
  const timerEl = document.getElementById(`timer-${id}`)

  if(action === "stop"){
    // APAGAR
    card.classList.remove("active")
    status.textContent = "APAGADO"
    clearInterval(intervals[id])
    timerEl.textContent = "00:00"
  }else{
    // ENCENDER
    card.classList.add("active")
    status.textContent = "RIEGO ACTIVO"
    timers[id] = Date.now()
    intervals[id] = setInterval(()=>{
      const elapsed = Math.floor((Date.now() - timers[id]) / 1000)
      timerEl.textContent = formatTime(elapsed)
    }, 1000)
  }

  // Refresca historial
  loadLog()
}

// ---------- RESTORE STATE ----------
function startTimer(id, startedAt){
  const card = document.getElementById(`zone-${id}`)
  const timerEl = document.getElementById(`timer-${id}`)
  const status = card.querySelector(".zone-status")
  const start = new Date(startedAt)

  card.classList.add("active")
  status.textContent = "RIEGO ACTIVO"

  intervals[id] = setInterval(()=>{
    const sec = Math.floor((Date.now() - start) / 1000)
    timerEl.textContent = formatTime(sec)
  }, 1000)
}

async function loadStatus(){
  const r = await fetch("/irrigation/status")
  const zones = await r.json()
  zones.forEach(z=>{
    if(z.is_active && z.started_at){
      startTimer(z.id, z.started_at)
    }
  })
}

// ---------- RIEGO PROGRAMADO ----------
async function loadSchedules(){
  const res = await fetch("/irrigation/schedule")
  const schedules = await res.json()
  const tbody = document.querySelector("#scheduleTable tbody")
  tbody.innerHTML = ""
  const noSchedules = document.getElementById("noSchedules")
  if(schedules.length === 0){
    noSchedules.textContent = "No hay riegos programados pendientes."
    return
  }
  noSchedules.textContent = ""
  schedules.forEach(s=>{
    const tr = document.createElement("tr")
    tr.innerHTML = `
      <td>${s.sector}</td>
      <td>${s.date}</td>
      <td>${s.start_time}</td>
      <td><button class="btn btn-danger btn-sm" onclick="cancelSchedule(${s.id})">Cancelar</button></td>
    `
    tbody.appendChild(tr)
  })
}

async function cancelSchedule(id){
  const res = await fetch(`/irrigation/schedule/${id}`, { method:"DELETE" })
  const data = await res.json()
  if(data.success) loadSchedules()
}

// Formulario de riego programado
document.getElementById("scheduleForm").addEventListener("submit", async (e)=>{
    e.preventDefault()

    const sector = document.getElementById("sector").value
    const date = document.getElementById("date").value
    const time = document.getElementById("time").value

    const r = await fetch("/irrigation/schedule", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({sector, date, time})
    })

    const res = await r.json()
    if(res.success){
        document.getElementById("scheduleForm").reset()
        loadSchedules()  // función para refrescar tabla via AJAX
    }else{
        alert(res.message || "Error al guardar")
    }
})


// ---------- HISTORIAL ----------
async function loadLog(){
  const res = await fetch("/irrigation/log")
  const logs = await res.json()
  const tbody = document.querySelector("#logTable tbody")
  tbody.innerHTML = ""
  const noLog = document.getElementById("noLog")
  if(logs.length === 0){
    noLog.textContent = "No hay historial de riegos."
    return
  }
  noLog.textContent = ""
  logs.forEach(l=>{
    const tr = document.createElement("tr")
    tr.innerHTML = `
      <td>${l.sector}</td>
      <td>${l.start_time}</td>
      <td>${l.end_time || "-"}</td>
      <td>${l.type.charAt(0).toUpperCase() + l.type.slice(1)}</td>
    `
    tbody.appendChild(tr)
  })
}

// ---------- INICIAL ----------
loadStatus()
loadSchedules()
loadLog()

// ---------- EXPORT ----------
window.toggleZone = toggleZone
window.cancelSchedule = cancelSchedule
