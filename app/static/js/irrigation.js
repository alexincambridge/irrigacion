const timers = {}
const intervals = {}

function formatTime(seconds){
  const m = String(Math.floor(seconds / 60)).padStart(2,"0")
  const s = String(seconds % 60).padStart(2,"0")
  return `${m}:${s}`
}

async function toggleZone(id){
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
}
