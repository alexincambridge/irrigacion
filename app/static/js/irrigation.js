async function createSchedule() {

    const sectorEl = document.getElementById("sector")
    const dateEl = document.getElementById("date")
    const startEl = document.getElementById("time")
    const endEl = document.getElementById("end_time")

    if(!sectorEl || !dateEl || !startEl || !endEl){
        console.error("Faltan elementos en el HTML")
        return
    }

    const sector = sectorEl.value
    const date = dateEl.value
    const start_time = startEl.value
    const end_time = endEl.value

    if(!sector || !date || !start_time || !end_time){
        alert("Completa todos los campos")
        return
    }

    if(end_time <= start_time){
        alert("La hora de fin debe ser mayor que la de inicio")
        return
    }

    const res = await fetch("/irrigation/schedule/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            sector,
            date,
            start_time,
            end_time
        })
    })

    if(res.ok){
        loadSchedules()
    } else {
        console.error("Error creando programación")
    }
}

async function loadSchedules(){

    const res = await fetch("/irrigation/schedule/list")
    const data = await res.json()

    const container = document.getElementById("scheduleList")

    if(data.length === 0){
        container.innerHTML = "<p>No hay riegos programados pendientes.</p>"
        return
    }

    let html = `
        <table>
        <tr>
            <th>Sector</th>
            <th>Fecha</th>
            <th>Inicio</th>
            <th>Fin</th>
            <th></th>
        </tr>
    `

    data.forEach(r => {
        html += `
        <tr>
            <td>${r.sector}</td>
            <td>${r.date}</td>
            <td>${r.start_time}</td>
            <td>${r.end_time}</td>
            <td>
                <button onclick="deleteSchedule(${r.id})">
                    Cancelar
                </button>
            </td>
        </tr>`
    })

    html += "</table>"

    container.innerHTML = html
}

async function deleteSchedule(id){

    await fetch(`/irrigation/schedule/delete/${id}`, {
        method: "DELETE"
    })

    loadSchedules()
}

async function manual(sector){

    await fetch(`/irrigation/manual/${sector}`, {
        method: "POST"
    })
}

loadSchedules()
