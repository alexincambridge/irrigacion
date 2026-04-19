# ⚡ Guía Rápida - Cambios en Riegos Programados

## 🎯 Cambios Principales

### 1. Auto-Desaparición ✨
- **Qué**: Riegos vencidos desaparecen automáticamente
- **Cómo**: schedule/list() detecta si `end_time <= ahora` y desactiva
- **Resultado**: No hay que limpiar manualmente, todo automático

### 2. Estado Dinámico 🟢
- **Regando**: Verde (● REGANDO) si `start_time <= ahora < end_time`
- **Espera**: Azul (◯ EN ESPERA) si `ahora < start_time`
- **Color**: Cambia automáticamente en tiempo real

### 3. Prioridad ⭐
- **Mostrado como**: ⭐ (1) ⭐⭐ (2) ⭐⭐⭐ (3)
- **Orden**: `ORDER BY priority DESC` (mayor prioridad primero)
- **Usuario puede cambiar**: Editar el campo priority en BD

### 4. Duración 📊
- **Cálculo**: `end_minutes - start_minutes`
- **Almacenado**: En campo `duration_minutes`
- **Mostrado**: "30 min", "75 min", etc.

### 5. Logs Automáticos 📋
- **Cuándo**: Al terminar el riego programado
- **Qué registra**: sector, start_time, end_time, duration, status='completado'
- **Tabla**: 6 columnas con toda la información

---

## 🗄️ Schema BD

### Tabla: irrigation_schedule
```sql
id                  -- ID único
sector              -- 1-4
date                -- YYYY-MM-DD
start_time          -- HH:MM
end_time            -- HH:MM (NUEVO)
duration_minutes    -- INT (NUEVO)
priority            -- INT 0-3 (NUEVO)
status              -- 'en espera' (NUEVO)
enabled             -- 1/0
created_at          -- timestamp
```

### Tabla: irrigation_log
```sql
id                  -- ID único
sector              -- 1-4
start_time          -- datetime
end_time            -- datetime
type                -- 'manual' o 'programado'
scheduled_id        -- FK a schedule (NUEVO)
duration_minutes    -- INT (NUEVO)
status              -- 'completado', 'activo' (NUEVO)
created_at          -- timestamp
```

---

## 🔧 Rutas Modificadas

### POST /irrigation/schedule/add
**Entrada:**
```json
{
  "sector": 1,
  "date": "2026-02-24",
  "start_time": "14:00",
  "end_time": "14:30"
}
```

**Servidor calcula:**
- `duration_minutes = 30`
- `status = 'en espera'`
- `priority = 0`

### GET /irrigation/schedule/list
**Proceso:**
1. Detecta riegos vencidos
2. Los registra en logs
3. Los marca como `enabled = 0`
4. Retorna solo activos (enabled = 1)

**Respuesta:**
```json
[
  {
    "id": 1,
    "sector": 1,
    "date": "2026-02-24",
    "start_time": "14:00",
    "end_time": "14:30",
    "duration_minutes": 30,
    "status": "en espera",
    "priority": 0,
    "enabled": 1
  }
]
```

### GET /irrigation/history/list
**Retorna:**
```json
[
  {
    "id": 1,
    "sector": 1,
    "start_time": "2026-02-24 14:00:00",
    "end_time": "2026-02-24 14:30:00",
    "duration_minutes": 30,
    "status": "completado",
    "type": "programado",
    "scheduled_id": 5
  }
]
```

---

## 🎨 Frontend - JavaScript

### renderSchedules()
```javascript
// Determina estado en tiempo real
const isActive = currentTotal >= startTotal && currentTotal < endTotal;
const status = isActive ? 'regando' : 'en espera';

// Colores dinámicos
const statusColor = isActive ? '#22c55e' : '#3b82f6';  // Verde/Azul
```

### renderHistory()
```javascript
// Tabla profesional
<table class="history-table">
  <thead>
    <th>Sector</th>
    <th>Inicio</th>
    <th>Fin</th>
    <th>Duración</th>
    <th>Tipo</th>
    <th>Estado</th>
  </thead>
  <tbody>
    <!-- Filas con datos completos -->
  </tbody>
</table>
```

---

## ⚙️ Backend - Scheduler

### app/scheduler.py
```python
# Cada 10 segundos busca riegos que terminaron
finished_rows = cur.execute("""
    SELECT id, sector, start_time, end_time, duration_minutes
    FROM irrigation_schedule
    WHERE date = ? AND enabled = 1 AND end_time <= ?
""", (today, now_time)).fetchall()

# Para cada uno que vencido:
# 1. Registra en irrigation_log con status='completado'
# 2. Marca como enabled=0
```

---

## 🎯 Estados Posibles

### Para schedule:
- `en espera` - Esperando su hora
- `regando` - Activo en este momento (calculado dinámicamente)
- `completado` - Ya terminó

### En logs (status):
- `completado` - Finalizó correctamente
- `activo` - Estaba en progreso
- (Se registra automáticamente)

---

## 🔄 Prioridades

### Sistema:
```
priority=0  → ⭐     (Baja)
priority=1  → ⭐⭐    (Media)
priority=2  → ⭐⭐⭐  (Alta)
priority=3+ → ⭐⭐⭐  (Máxima)
```

### Cómo cambiar:
```sql
UPDATE irrigation_schedule
SET priority = 2
WHERE id = 5;
```

---

## 📊 Visualización

### Riegos Programados (Tabla):
```
⭐  Sector 1 - Jardín    14:00-14:30   30 min   ● REGANDO   [Cancelar]
⭐⭐ Sector 2 - Huerta    14:30-15:00   30 min   ◯ EN ESPERA [Cancelar]
⭐⭐⭐ Sector 3 - Césped   15:00-15:30   30 min   ◯ EN ESPERA [Cancelar]
```

### Logs (Tabla):
```
Sector 1-Jard     Feb 24, 14:00     Feb 24, 14:30    30 min   📅   COMPLETADO
Sector 2-Huer     Feb 24, 14:30     Feb 24, 15:00    30 min   📅   COMPLETADO
Sector 3-Cés      Feb 24, 14:00     Feb 24, 14:45    45 min   👤   COMPLETADO
```

---

## 🚀 Testing

### Verificar auto-desaparición:
```bash
1. Programa riego para hace 5 min
2. schedule/list() lo detecta como vencido
3. Lo registra en logs
4. Lo marca como enabled=0
5. Desaparece de la vista
6. Aparece en logs
```

### Verificar estado:
```bash
1. Si ahora está entre start_time y end_time → "REGANDO"
2. Si ahora es antes de start_time → "EN ESPERA"
3. Si ahora es después de end_time → No aparece (fue desactivado)
```

### Verificar tabla de logs:
```bash
1. Completa un riego
2. Verifica que aparezca en logs
3. Todos los campos deben estar llenos
4. Duración debe estar en minutos
5. Estado debe ser "COMPLETADO"
```

---

## 💡 Tips

### Para resetear la BD:
```bash
python scripts/init_db.py
```

### Para ver en BD:
```bash
sqlite3 instance/irrigation.db
SELECT * FROM irrigation_schedule WHERE enabled = 1;
SELECT * FROM irrigation_log ORDER BY id DESC LIMIT 10;
```

### Para debug:
```javascript
// En browser console
console.log(schedulesData);  // Ver datos actuales
console.log(historyData);    // Ver historial
```

---

## ✅ Checklist de Implementación

- [x] Auto-desaparición de vencidos
- [x] Estado dinámico (regando/espera)
- [x] Prioridad visible (⭐)
- [x] Duración en minutos
- [x] Auto-registro en logs
- [x] Tabla de logs completa
- [x] Colores dinámicos
- [x] Scheduler actualizado
- [x] BD actualizada
- [x] Frontend actualizado

---

**¡Todo implementado y listo para usar!** 🎉

