const timers = {}
const intervals = {}

// ---------- UTIL ----------
function formatTime(seconds){
  const m = String(Math.floor(seconds / 60)).padStart(2,"0")
  const s = String(seconds % 60).padStart(2,"0")
  return `${m}:${s}`
}

// ---------- TOGGLE ----------
async function toggleZone(id){
  const r = await fetch(`/irrigation/toggle/${id}`, { method:"POST" })
  if(!r.ok) return

  const card = document.getElementById(`zone-${id}`)
  const status = card.querySelector(".zone-status")
  const timerEl = document.getElementById(`timer-${id}`)

  if(card.classList.contains("active")){
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

loadStatus()

// ---------- EXPORT ----------
window.toggleZone = toggleZone
