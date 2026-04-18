# 🗄️ Guía de Base de Datos - Sistema de Riego

## 🚀 Recrear la Base de Datos

### Opción 1: Script Mejorado (RECOMENDADO)
```bash
python3 scripts/init_db_clean.py
```

**Ventajas:**
- ✅ Más clara y documentada
- ✅ Muestra cada tabla que crea
- ✅ Mejor para entender qué hace

### Opción 2: Script Original
```bash
python3 scripts/init_db.py
```

**Ventajas:**
- ✅ El que has estado usando
- ✅ Funciona perfectamente

---

## 📊 Tablas que se Crean

### 1. **irrigation_zones** (Zonas de riego)
```sql
id | name      | gpio_pin | enabled
1  | Jardín    | 23       | 1
2  | Huerta    | 24       | 1
3  | Césped    | 25       | 1
4  | Árboles   | 27       | 1
```

### 2. **irrigation_schedule** (Riegos programados)
```sql
id | sector | date | start_time | end_time | duration_minutes | 
   | priority | status | repeat_days | repeat_enabled | origin | enabled | created_at
```

Campos importantes:
- `sector` → Zona (1-4)
- `start_time` → Hora inicio (ej: "14:30")
- `end_time` → Hora fin
- `duration_minutes` → Duración
- `status` → 'en espera', 'regando', 'completado'
- `repeat_days` → Días repetición (LMXJVSD)
- `repeat_enabled` → 0/1 para activar repetición
- `origin` → 'manual' o 'programado'

### 3. **irrigation_log** (Historial de riegos)
```sql
id | sector | start_time | end_time | type | scheduled_id | 
   | duration_minutes | status | created_at
```

### 4. **water_consumption** (Consumo de agua)
```sql
id | irrigation_id | liters | cost | timestamp
```

### 5. **sensor_data** (Datos de sensores adicionales)
```sql
id | temperature | humidity | solar | pressure | ec | ph | created_at
```

Campos:
- `temperature` → °C
- `humidity` → %
- `solar` → W/m²
- `pressure` → hPa
- `ec` → mS/cm (conductividad)
- `ph` → pH del agua

### 6. **dht_readings** (DHT22 - Temperatura/Humedad)
```sql
id | temperature | humidity | created_at
```

Datos reales del sensor DHT22 cada 2 segundos.

### 7. **irrigation_records** (Registros detallados)
```sql
id | sector | start_datetime | end_datetime | type
```

Campos:
- `type` → 'manual' o 'programado'

---

## 🔧 Ejecutar el Script

### Paso 1: Ubicarse en la carpeta correcta
```bash
cd /path/to/irrigacion
```

### Paso 2: Ejecutar el script
```bash
# Opción A (mejorado)
python3 scripts/init_db_clean.py

# Opción B (original)
python3 scripts/init_db.py
```

### Paso 3: Verificar que funcionó
```bash
# Ver las tablas creadas
sqlite3 instance/irrigation.db ".tables"

# Ver la estructura de una tabla
sqlite3 instance/irrigation.db ".schema dht_readings"

# Contar registros
sqlite3 instance/irrigation.db "SELECT COUNT(*) FROM irrigation_zones;"
```

---

## 📝 Lo Que Hace el Script

1. ✅ Crea carpeta `instance/` si no existe
2. ✅ Elimina BD antigua (si existe)
3. ✅ Crea 7 tablas necesarias
4. ✅ Inserta 4 zonas por defecto
5. ✅ Confirma cambios en BD

---

## 🚨 Advertencias Importantes

⚠️ **CUIDADO:** El script **ELIMINA** la BD existente
- Si tienes datos importantes, **GUARDA COPIAS** primero
- No ejecutes si tienes historiales que necesites

✅ **SEGURO:** La carpeta `instance/` se crea automáticamente

---

## 📊 Ejemplo: Verificar Datos

```bash
# Ver todas las zonas
sqlite3 instance/irrigation.db "SELECT * FROM irrigation_zones;"

# Ver riegos programados
sqlite3 instance/irrigation.db "SELECT * FROM irrigation_schedule;"

# Ver últimas 5 lecturas DHT22
sqlite3 instance/irrigation.db "SELECT * FROM dht_readings ORDER BY id DESC LIMIT 5;"

# Ver consumo total de agua
sqlite3 instance/irrigation.db "SELECT SUM(liters) FROM water_consumption;"
```

---

## 🛠️ Si Algo Falla

### Error: "No such table"
→ Ejecuta `python3 scripts/init_db_clean.py` de nuevo

### Error: "Permission denied"
→ Cambia permisos: `chmod +x scripts/init_db_clean.py`

### Error: "sqlite3 not found"
→ Instala sqlite3: `sudo apt install sqlite3`

---

## ✅ Checklist

- [ ] Ejecutaste: `python3 scripts/init_db_clean.py`
- [ ] Verificaste: `sqlite3 instance/irrigation.db ".tables"`
- [ ] Ves 7 tablas: irrigation_zones, irrigation_schedule, irrigation_log, etc.
- [ ] Verificaste zonas: `sqlite3 instance/irrigation.db "SELECT * FROM irrigation_zones;"`
- [ ] Ves 4 zonas: Jardín, Huerta, Césped, Árboles

---

## 📚 Referencias

- Script mejorado: `scripts/init_db_clean.py`
- Script original: `scripts/init_db.py`
- BD: `instance/irrigation.db`

---

> **Última actualización:** 25 de Marzo de 2026  
> **Estado:** ✅ Listo para usar

