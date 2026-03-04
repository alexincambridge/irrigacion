document.addEventListener('DOMContentLoaded', function() {

    // --- Data Definition for Avocado in Costa Tropical (Southern Spain) ---
    const scheduleData = [
        { // 0: Enero
            season: "Invierno",
            stage: "Reposo / Cosecha Tardía",
            recommendation: "Mantenimiento. Si no hay heladas, ligera aportación de N.",
            tasks: ["Revisar sistema de riego", "Poda de limpieza (si aplica)", "Cosecha de variedades tempranas"],
            recipe: "Nitrato Potásico (Baja dosis)",
            badge: "bg-secondary",
            npk: "5-5-5"
        },
        { // 1: Febrero
            season: "Invierno Tardío",
            stage: "Pre-floración / Inducción Floral",
            recommendation: "Inicio de actividad. Aportar Zinc y Boro para la floración.",
            tasks: ["Aplicación foliar de Boro y Zinc", "Primer riego de apoyo"],
            recipe: "Zinc + Boro + Aminoácidos",
            badge: "bg-info",
            npk: "10-5-5 + Zn, B"
        },
        { // 2: Marzo
            season: "Primavera",
            stage: "Floración Plena",
            recommendation: "Demanda alta de Nitrógeno para brotación. Cuidado con el estrés hídrico.",
            tasks: ["Aumentar frecuencia de riego", "Quelato de Hierro (Fe-EDDHA)"],
            recipe: "Nitrato Amónico + Quelato Fe",
            badge: "bg-success",
            npk: "20-5-5"
        },
        { // 3: Abril
            season: "Primavera",
            stage: "Cuajado del Fruto",
            recommendation: "Evitar excesos de Nitrógeno que tiren la flor. Mantener humedad constante.",
            tasks: ["Control de plagas (trips)", "Mantener suelo húmedo"],
            recipe: "Equilibrio (20-20-20) suave",
            badge: "bg-success",
            npk: "15-15-15"
        },
        { // 4: Mayo
            season: "Primavera Tardía",
            stage: "Caída de Pétalos / Frutito",
            recommendation: "El fruto está cuajando. Aportar Calcio para estructura celular.",
            tasks: ["Nitrato de Calcio", "Vigilancia de purga (caída natural)"],
            recipe: "Nitrato de Calcio",
            badge: "bg-success",
            npk: "15-5-20 + Ca"
        },
        { // 5: Junio
            season: "Verano",
            stage: "Crecimiento Rápido del Fruto (I)",
            recommendation: "Máxima demanda hídrica y nutricional. Aumentar dosis.",
            tasks: ["Riegos diarios o muy frecuentes", "Aporte de NPK equilibrado"],
            recipe: "NPK 20-10-20",
            badge: "bg-warning",
            npk: "20-10-20"
        },
        { // 6: Julio
            season: "Verano",
            stage: "Crecimiento Rápido del Fruto (II)",
            recommendation: "Cuidado con golpes de calor. Potasio empieza a ser importante.",
            tasks: ["Vigilar quemaduras de sol", "Riego abundante"],
            recipe: "NPK 15-5-25",
            badge: "bg-danger",
            npk: "15-5-25"
        },
        { // 7: Agosto
            season: "Verano",
            stage: "Crecimiento Rápido del Fruto (III)",
            recommendation: "Continuar con NPK y microelementos (Mg, Mn).",
            tasks: ["Aporte de Sulfato de Magnesio", "Corrección de Zinc si necesario"],
            recipe: "NPK + Magnesio",
            badge: "bg-danger",
            npk: "15-5-25 + Mg"
        },
        { // 8: Septiembre
            season: "Otoño",
            stage: "Engorde y Acumulación de Reservas",
            recommendation: "Aumentar Potasio (K) para calibre. Disminuir Nitrógeno.",
            tasks: ["Potasio foliar o fertirrigación", "Preparar árbol para invierno"],
            recipe: "Sulfato Potásico / Nitrato Potásico",
            badge: "bg-warning",
            npk: "5-10-30"
        },
        { // 9: Octubre
            season: "Otoño",
            stage: "Maduración (Variedades Tempranas)",
            recommendation: "Poco Nitrógeno. Mantener Potasio y Fósforo para raíces.",
            tasks: ["No forzar brotación tardía", "Limpieza de hierbas"],
            recipe: "Fósforo + Potasio (PK)",
            badge: "bg-secondary",
            npk: "0-20-30"
        },
        { // 10: Noviembre
            season: "Otoño",
            stage: "Pre-Reposo / Cosecha",
            recommendation: "Riegos más espaciados. Solo mantenimiento.",
            tasks: ["Inicio de recolección (algunas var.)", "Control de hongos"],
            recipe: "Mantenimiento suave",
            badge: "bg-secondary",
            npk: "-"
        },
        { // 11: Diciembre
            season: "Invierno",
            stage: "Reposo Invernal",
            recommendation: "Mínima actividad. No fertilizar si hace frío.",
            tasks: ["Protección contra heladas", "Revisión de goteros"],
            recipe: "Ninguna",
            badge: "bg-light text-dark",
            npk: "-"
        }
    ];

    // --- References ---
    const dateDisplay = document.getElementById('current-date-display');
    const seasonBadge = document.getElementById('current-season-badge');
    const stageDiv = document.getElementById('current-stage');
    const recList = document.getElementById('current-recommendation-list');
    const scheduleBody = document.getElementById('schedule-body');
    const monthSelector = document.getElementById('month-selector');
    const form = document.getElementById('fertilization-form');

    // --- Helper Functions ---
    const months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

    function updateUI(monthIndex) {
        const data = scheduleData[monthIndex];

        // Update header
        const now = new Date();
        // If selected month is current month, show full date, else just month
        if (monthIndex === now.getMonth()) {
            dateDisplay.textContent = now.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        } else {
            dateDisplay.textContent = months[monthIndex] + " (Visualización)";
        }

        seasonBadge.textContent = data.season;
        seasonBadge.className = `badge ${data.badge}`;

        // Update Current Status Card
        stageDiv.innerHTML = `<h3 class="mb-0 text-primary">${data.stage}</h3><small class="text-muted">Receta recomendada: <strong>${data.recipe}</strong></small>`;

        recList.innerHTML = "";

        // Add recommendation text
        const liRec = document.createElement("li");
        liRec.className = "mb-2";
        liRec.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i> ${data.recommendation}`;
        recList.appendChild(liRec);

        // Add NPK
        const liNpk = document.createElement("li");
        liNpk.className = "mb-2";
        liNpk.innerHTML = `<i class="fas fa-flask text-warning me-2"></i> <span class="fw-bold">NPK Sugerido:</span> ${data.npk}`;
        recList.appendChild(liNpk);

        // Add tasks
        data.tasks.forEach(task => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fas fa-angle-right text-muted me-2"></i> ${task}`;
            recList.appendChild(li);
        });

        // Update Table Selection
        renderTable(monthIndex);
    }

    function renderTable(selectedMonthIndex) {
        scheduleBody.innerHTML = "";

        scheduleData.forEach((data, index) => {
            const row = document.createElement("tr");

            // Highlight selected month
            if (index === selectedMonthIndex) {
                row.className = "table-primary border-primary";
            } else if (index === new Date().getMonth()) {
                row.className = "table-light"; // Current month (if different from selected)
            }

            row.innerHTML = `
                <td>
                    <div class="fw-bold">${months[index]}</div>
                    <small class="text-muted">${data.season}</small>
                </td>
                <td>
                    <span class="badge ${data.badge}">${data.stage}</span>
                </td>
                <td>
                    <div><strong>${data.recipe}</strong></div>
                    <small class="text-muted d-block text-truncate" style="max-width: 250px;">${data.recommendation}</small>
                </td>
                <td>
                    <div class="small fw-bold text-muted">NPK: ${data.npk}</div>
                </td>
            `;

            // Allow click to select
            row.style.cursor = "pointer";
            row.onclick = () => {
                monthSelector.value = index;
                updateUI(index);
            };

            scheduleBody.appendChild(row);
        });
    }

    // --- Initialization ---
    const currentMonth = new Date().getMonth();
    monthSelector.value = currentMonth;
    updateUI(currentMonth);

    // --- Event Listeners ---
    monthSelector.addEventListener('change', (e) => {
        updateUI(parseInt(e.target.value));
    });

    // Handle Form Submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const duration = document.getElementById('duration').value;
        const currentData = scheduleData[parseInt(monthSelector.value)];
        const btn = form.querySelector('button');
        const originalText = btn.innerHTML;

        // Disable button
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Iniciando...`;

        try {
            const response = await fetch('/api/fertilize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipe: currentData.recipe,
                    duration: parseInt(duration)
                })
            });

            const result = await response.json();

            if (result.success) {
                // Show success toast or alert
                 const alertDiv = document.createElement('div');
                 alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
                 alertDiv.innerHTML = `
                    <strong><i class="fas fa-check"></i> Éxito!</strong> ${result.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                 `;
                 form.parentNode.insertBefore(alertDiv, form.nextSibling);

                 // Auto dismiss
                 setTimeout(() => alertDiv.remove(), 5000);
            } else {
                alert("Error al iniciar fertilización: " + (result.error || "Desconocido"));
            }

        } catch (error) {
            console.error('Error:', error);
            alert("Error de conexión");
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    });

});

