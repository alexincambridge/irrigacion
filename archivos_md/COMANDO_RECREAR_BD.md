# 🚀 COMANDO RÁPIDO - Recrear Base de Datos

## ⚡ Copiar y Pegar

```bash
cd /Users/alexg/Sites/irrigacion && python3 scripts/init_db_clean.py
```

O si prefieres el script original:

```bash
cd /Users/alexg/Sites/irrigacion && python3 scripts/init_db.py
```

---

## ✅ Qué Pasará

```
🛠️  Creando tablas de la base de datos...
============================================================
📍 Tabla: irrigation_zones (Zonas de riego)
   ✅ 4 zonas creadas: Jardín, Huerta, Césped, Árboles
⏰ Tabla: irrigation_schedule (Riegos programados)
   ✅ Tabla creada para programación de riegos
📋 Tabla: irrigation_log (Historial de riegos)
   ✅ Tabla creada para historial de riegos
💧 Tabla: water_consumption (Consumo de agua)
   ✅ Tabla creada para consumo de agua
📊 Tabla: sensor_data (Datos de sensores adicionales)
   ✅ Tabla creada: temperatura, humedad, solar, presión, EC, pH
🌡️  Tabla: dht_readings (DHT22 - Temperatura/Humedad)
   ✅ Tabla creada para DHT22
📈 Tabla: irrigation_records (Registros detallados)
   ✅ Tabla creada para registros de riegos
============================================================
✅ Base de datos inicializada correctamente
📁 Ubicación: instance/irrigation.db
============================================================

🎉 Listo para usar
```

---

## 📊 Verificar que Funcionó

```bash
sqlite3 /Users/alexg/Sites/irrigacion/instance/irrigation.db "SELECT * FROM irrigation_zones;"
```

Debería mostrar:
```
1|Jardín|23|1
2|Huerta|24|1
3|Césped|25|1
4|Árboles|27|1
```

---

## 📁 Estructura Creada

```
irrigacion/
└── instance/
    └── irrigation.db (recreada ✨)
        ├── irrigation_zones (4 zonas)
        ├── irrigation_schedule (riegos programados)
        ├── irrigation_log (historial)
        ├── water_consumption (agua usada)
        ├── sensor_data (sensores)
        ├── dht_readings (DHT22)
        └── irrigation_records (registros)
```

---

## ⚠️ Importante

**El script ELIMINA la BD existente**

Si tienes datos que conservar:
```bash
cp /Users/alexg/Sites/irrigacion/instance/irrigation.db /Users/alexg/Sites/irrigacion/instance/irrigation.db.bak
```

Luego ejecuta:
```bash
cd /Users/alexg/Sites/irrigacion && python3 scripts/init_db_clean.py
```

---

## 🎯 Scripts Disponibles

| Script | Ubicación | Descripción |
|---|---|---|
| **init_db_clean.py** | `scripts/init_db_clean.py` | Versión mejorada (RECOMENDADA) |
| **init_db.py** | `scripts/init_db.py` | Versión original |

Ambos crean exactamente la misma BD.

---

> Listo para ejecutar! 🚀

