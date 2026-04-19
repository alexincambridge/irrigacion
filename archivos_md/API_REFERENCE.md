# 📡 API ENDPOINTS REFERENCE

## Base URL: `http://localhost:5000`

---

## 🔐 AUTHENTICATION
Todos los endpoints requieren estar logueado (excepto `/login` y `/register`)

---

## 📊 DASHBOARD

### GET `/dashboard`
Página HTML del dashboard
```
Response: HTML page
```

### GET `/dashboard/data`
Obtener datos actuales de sensores
```
Response:
{
  "temperature": 25.5,
  "humidity": 65,
  "solar": 850,
  "pressure": 1015,
  "ec": 1.2,
  "ph": 6.8,
  "time": "2026-03-02 14:30:00",
  "water_liters": 150.5,
  "dht_temperature": 24.8,
  "dht_humidity": 62
}
```

### GET `/dashboard/history`
Obtener histórico de sensores (últimas 24 horas)
```
Response:
[
  {
    "temperature": 25.5,
    "humidity": 65,
    "pressure": 1015,
    "solar": 850,
    "ec": 1.2,
    "ph": 6.8,
    "timestamp": "2026-03-02 14:30:00"
  },
  ...
]
```

---

## 💧 IRRIGATION

### GET `/irrigation`
Página HTML del sistema de riego
```
Response: HTML page
```

### GET `/irrigation/zones/status`
Obtener estado de todas las zonas
```
Response:
{
  "success": true,
  "zones": {
    "1": {"active": true, "duration": 1200},
    "2": {"active": false, "duration": 0},
    "3": {"active": true, "duration": 800},
    "4": {"active": false, "duration": 0}
  }
}
```

### POST `/irrigation/manual/<zone_id>`
Activar/desactivar riego manual de una zona
```
URL: /irrigation/manual/1
Response:
{
  "success": true,
  "active": true,
  "sector": 1
}
```

### GET `/irrigation/schedule/list`
Obtener riegos programados pendientes
```
Response:
[
  {
    "id": 1,
    "sector": 1,
    "date": "2026-03-02",
    "start_time": "14:00",
    "end_time": "14:30",
    "duration_minutes": 30,
    "priority": 0,
    "status": "en espera",
    "repeat_days": "LMXJVSD",
    "repeat_enabled": 1,
    "origin": "programado",
    "enabled": 1
  },
  ...
]
```

### POST `/irrigation/schedule/add`
Crear nuevo riego programado
```
Body:
{
  "sector": 1,
  "date": "2026-03-02",
  "start_time": "14:00",
  "end_time": "14:30",
  "repeat_days": "LMXJVSD",
  "repeat_enabled": 1,
  "origin": "programado"
}

Response:
{
  "success": true
}
```

### DELETE `/irrigation/schedule/delete/<schedule_id>`
Cancelar un riego programado
```
Response:
{
  "success": true
}
```

### GET `/irrigation/history/list`
Obtener historial de riegos
```
Response:
[
  {
    "id": 1,
    "sector": 1,
    "start_time": "2026-03-02 14:00:00",
    "end_time": "2026-03-02 14:30:00",
    "type": "programado",
    "duration_minutes": 30,
    "status": "completado",
    "scheduled_id": 1
  },
  ...
]
```

### POST `/irrigation/emergency-stop`
Detener TODOS los riegos inmediatamente
```
Response:
{
  "success": true,
  "message": "All zones stopped"
}
```

---

## 📋 LOGS

### GET `/logs`
Página HTML del historial de logs
```
Response: HTML page
```

### GET `/irrigation/history/list`
(Ver en sección IRRIGATION - mismo endpoint usado por logs)

---

## 💻 SYSTEM

### GET `/system`
Página HTML de información del sistema
```
Response: HTML page
```

### GET `/system/internet-check`
Verificar conectividad a internet
```
Response:
{
  "connected": true,
  "public_ip": "203.0.113.45",
  "isp": "ISP Name Inc."
}
```

### GET `/system/esp32-devices`
Escanear dispositivos ESP32 en la red
```
Response:
{
  "devices": [
    {
      "name": "ESP32-1",
      "ip": "192.168.1.100",
      "mac": "AA:BB:CC:DD:EE:01",
      "zones": 4,
      "online": true,
      "last_seen": "Ahora"
    },
    ...
  ]
}
```

### GET `/system/water-total`
Obtener consumo total de agua
```
Response:
{
  "total": 1250.5
}
```

### GET `/system/logs-count`
Obtener número total de logs
```
Response:
{
  "count": 145
}
```

---

## 👤 USER

### GET `/api/current-user`
Obtener información del usuario actual
```
Response:
{
  "username": "admin",
  "email": "admin@example.com"
}
```

### GET `/login`
Página de login
```
Response: HTML page
```

### POST `/login`
Enviar credenciales de login
```
Body:
{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "success": true,
  "message": "Login successful"
}
```

### GET `/logout`
Cerrar sesión
```
Response: Redirección a /login
```

---

## 🌊 WATER

### GET `/water`
Página de consumo de agua
```
Response: HTML page
```

### GET `/water/data`
Obtener datos de consumo de agua
```
Response:
[
  {
    "time": "2026-03-02 14:00:00",
    "liters": 12.5
  },
  ...
]
```

---

## 📡 LORA (PRÓXIMAMENTE)

### POST `/lora/command/<device_id>`
Enviar comando LoRa a dispositivo ESP32
```
Body:
{
  "command": "ZONE_ON",
  "zone_id": 1,
  "duration_minutes": 30
}

Response:
{
  "success": true,
  "device_id": 1,
  "command": "ZONE_ON"
}
```

### GET `/lora/devices/status`
Obtener estado de dispositivos LoRa
```
Response:
{
  "devices": [
    {
      "id": 1,
      "name": "ESP32-Sectores",
      "online": true,
      "rssi": -85,
      "last_packet": "2026-03-02 14:35:00",
      "zones": {
        "1": {"state": "ON", "duration": 1200},
        "2": {"state": "OFF", "duration": 0},
        "3": {"state": "ON", "duration": 800},
        "4": {"state": "OFF", "duration": 0}
      }
    }
  ]
}
```

---

## ⚠️ ERROR RESPONSES

### 400 - Bad Request
```json
{
  "error": "Invalid parameters"
}
```

### 401 - Unauthorized
```json
{
  "error": "Login required"
}
```

### 404 - Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 - Server Error
```json
{
  "error": "Internal server error"
}
```

---

## 🔄 HEADERS RECOMENDADOS

```
Content-Type: application/json
Accept: application/json
```

---

## 📝 NOTAS

- Todos los timestamps están en formato ISO 8601: `YYYY-MM-DD HH:MM:SS`
- Los booleanos se envían como `true`/`false` en JSON
- Los IDs están en el rango 1-4 para zonas
- La prioridad de riego es: 1=Árboles (más alta) → 4=Césped (más baja)

---

**Última actualización:** 2 de Marzo de 2026
**Versión API:** 4.0

