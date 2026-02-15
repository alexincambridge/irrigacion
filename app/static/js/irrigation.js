async function createSchedule() {

    const sector = document.getElementById("sector").value
    const date = document.getElementById("date").value
    const time = document.getElementById("time").value

    const res = await fetch("/irrigation/schedule/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({sector, date, time})
    })

    if(res.ok){
        loadSchedules()
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

    let html = "<table><tr><th>Sector</th><th>Fecha</th><th>Hora</th><th></th></tr>"

    data.forEach(r => {
        html += `
        <tr>
            <td>${r.sector}</td>
            <td>${r.date}</td>
            <td>${r.time}</td>
            <td><button onclick="deleteSchedule(${r.id})">Cancelar</button></td>
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
