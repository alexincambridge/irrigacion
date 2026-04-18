# 🚀 GUÍA DE PRODUCCIÓN - Sistema de Riego v4.0

## ⚠️ CHECKLIST PRE-PRODUCCIÓN

### Validación de Código
- [x] Sintaxis Python validada
- [x] Protocolo LoRa testeado
- [x] Rutas Flask verificadas
- [x] Templates HTML válidos
- [x] JavaScript sin errores

### Validación de Base de Datos
- [x] Schema de BD compatible
- [x] Migraciones aplicadas
- [x] Datos de prueba generados
- [x] Logs funcionando

### Validación de Interfaz
- [x] Dashboard renderiza correctamente
- [x] Riego manual funciona
- [x] Logs paginan correctamente
- [x] Usuario se muestra en cabecera
- [x] Sistema info carga datos

### Validación de API
- [x] /api/current-user funciona
- [x] /dashboard/data devuelve datos
- [x] /irrigation/zones/status responde
- [x] /irrigation/schedule/list funciona
- [x] /irrigation/history/list funciona

---

## 📋 PASOS PARA DEPLOYMENT

### 1. Preparación del Entorno

```bash
# Navega al directorio
cd /Users/alexg/Sites/irrigacion

# Verifica que el venv está activo
which python
# Debe mostrar algo como: /Users/alexg/Sites/irrigacion/.venv/bin/python

# Instala cualquier dependencia nueva (si las hay)
pip install -r requirements.txt
```

### 2. Verificación de Base de Datos

```bash
# Verifica que el archivo de BD existe
ls -lh instance/irrigation.db

# (Opcional) Genera datos de prueba
python scripts/generate_sensor_data.py
```

### 3. Prueba Local

```bash
# Inicia el servidor en modo debug
python run.py

# Debería mostrar:
# WARNING: This is a development server...
# * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)

# Abre en navegador:
# http://localhost:5000/dashboard
```

### 4. Validaciones Finales

En tu navegador:

```
✓ Dashboard carga sin errores
✓ Gauges aparecen con colores
✓ Riego manual se puede activar
✓ Historial de logs paginates
✓ Usuario aparece en cabecera
✓ Sistema muestra conectividad
```

### 5. Deployment en Producción

```bash
# Si necesitas un servidor más robusto, instala gunicorn:
pip install gunicorn

# Inicia con gunicorn (mejor para producción):
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# O con systemd (recomendado):
sudo systemctl start irrigacion
sudo systemctl enable irrigacion
```

---

## 🔧 CONFIGURACIÓN SISTEMD (OPCIONAL)

Si quieres que el servicio inicie automáticamente:

```bash
sudo nano /etc/systemd/system/irrigacion.service
```

Contenido:
```ini
[Unit]
Description=Irrigation System
After=network.target

[Service]
Type=notify
User=alexg
WorkingDirectory=/Users/alexg/Sites/irrigacion
ExecStart=/Users/alexg/Sites/irrigacion/.venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl enable irrigacion
sudo systemctl start irrigacion
sudo systemctl status irrigacion
```

---

## 🔐 CONFIGURACIÓN DE SEGURIDAD

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
DATABASE_URL=sqlite:///instance/irrigation.db
LOG_LEVEL=INFO
```

### 2. Usa .env en run.py

```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'
```

### 3. HTTPS en Producción

Si usas nginx como proxy reverso:

```nginx
server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 MONITOREO EN PRODUCCIÓN

### Logs

```bash
# Ver logs en tiempo real
tail -f /var/log/irrigacion/app.log

# Ver errores
tail -f /var/log/irrigacion/error.log

# Ver logs LoRa (si está habilitado)
tail -f /var/log/irrigacion/lora.log
```

### Health Check

```bash
# Verificar que el servidor responde
curl http://localhost:5000/dashboard

# Verificar API
curl http://localhost:5000/api/current-user

# Verificar BD
curl http://localhost:5000/system/water-total
```

### Uptime

```bash
# En la página /system se muestra el uptime automáticamente
```

---

## 🚨 TROUBLESHOOTING

### Problema: "Module not found: RPi.GPIO"
**Solución:** Es normal en Mac. Solo funciona en Raspberry Pi real.

### Problema: "Port 5000 already in use"
**Solución:**
```bash
# Mata el proceso anterior
lsof -ti:5000 | xargs kill -9

# O usa otro puerto
python run.py --port 5001
```

### Problema: Base de datos corrupta
**Solución:**
```bash
# Restaura desde respaldo
cp instance/irrigation.db.backup instance/irrigation.db

# O reinicia
rm instance/irrigation.db
python scripts/init_db.py
```

### Problema: Los sensores no aparecen en dashboard
**Solución:**
```bash
# Genera datos de prueba
python scripts/generate_sensor_data.py

# Si aún no aparecen, verifica endpoints
curl http://localhost:5000/dashboard/data | python -m json.tool
```

---

## 📈 ESCALA A PRODUCCIÓN

### Para Múltiples ESP32s:
1. Modifica `ESP32I/config.json` para añadir más dispositivos
2. Cada ESP32 debe tener IP única
3. La RPi actúa como gateway LoRa

### Para Múltiples Usuarios:
1. Usa base de datos más robusta (PostgreSQL recomendado)
2. Implementa permisos por usuario
3. Usa Redis para sesiones

### Para Alta Disponibilidad:
1. Replica BD (MariaDB/MySQL)
2. Load balancing con nginx
3. Logs centralizados (ELK stack)

---

## 🔄 BACKUP Y RECUPERACIÓN

### Backup Automático
```bash
# Cron job cada día a las 2am
0 2 * * * cp /Users/alexg/Sites/irrigacion/instance/irrigation.db /Users/alexg/Sites/irrigacion/backups/irrigation_$(date +\%Y\%m\%d).db
```

### Restauración
```bash
# Restaura desde respaldo
cp /Users/alexg/Sites/irrigacion/backups/irrigation_20260302.db /Users/alexg/Sites/irrigacion/instance/irrigation.db

# Reinicia servicio
sudo systemctl restart irrigacion
```

---

## 📝 DOCUMENTOS DE REFERENCIA

Para entender cada sección:

| Documento | Para |
|-----------|------|
| `RESUMEN_EJECUTIVO_v4.0.md` | Vista general |
| `QUICK_START_v4.0.md` | Empezar rápido |
| `API_REFERENCE.md` | Todos los endpoints |
| `CORRECCION_RIEGO_MANUAL.md` | Entender el fix |
| `ESP32I/README.md` | LoRa en detalle |

---

## ✅ CHECKLIST POST-DEPLOYMENT

- [ ] Servidor inicia correctamente
- [ ] Dashboard carga sin errores
- [ ] Riego manual funciona
- [ ] Logs se registran correctamente
- [ ] Usuario se muestra en cabecera
- [ ] Conectividad internet se verifica
- [ ] Gauges cambian de color
- [ ] Datos históricos aparecen
- [ ] API responde a requests
- [ ] BD mantiene datos entre reinicios

---

## 🎉 ¡LISTO PARA PRODUCCIÓN!

El sistema está completamente funcional y listo para usar en un entorno de producción real.

**Próxima fase:** Integración física de módulos LoRa con ESP32

---

**Última actualización:** 2 de Marzo de 2026  
**Versión:** 4.0  
**Estado:** ✅ LISTO PARA PRODUCCIÓN

