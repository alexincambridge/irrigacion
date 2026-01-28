async function refreshStatus(){
  const r = await fetch("/irrigation/status")
  const d = await r.json()

  const s = document.getElementById("status")
  if(d.on){
    s.innerText = "ENCENDIDO"
    s.style.color = "green"
  }else{
    s.innerText = "APAGADO"
    s.style.color = "red"
  }
}

document.getElementById("btnOn").onclick = async ()=>{
  await fetch("/irrigation/on", {method:"POST"})
  refreshStatus()
}

document.getElementById("btnOff").onclick = async ()=>{
  await fetch("/irrigation/off", {method:"POST"})
  refreshStatus()
}

refreshStatus()
setInterval(refreshStatus, 3000)
