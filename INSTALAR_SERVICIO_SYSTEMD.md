# 🔧 CONFIGURAR SERVICIO SYSTEMD - irrigacion.service

## El Problema
```
Failed to restart irrigacion.service: Unit irrigacion.service not found.
```

El servicio no está creado en systemd.

## La Solución

### Paso 1: Copia el archivo del servicio
```bash
# En tu RPi
cd /home/alexdev/Documents/irrigacion

# Descarga o copia el archivo irrigacion.service
# (Debe estar en la raíz del proyecto)
ls irrigacion.service  # Verifica que exista
```

### Paso 2: Instala el servicio
```bash
# Copia el archivo a systemd
sudo cp irrigacion.service /etc/systemd/system/irrigacion.service

# Dale permisos correctos
sudo chmod 644 /etc/systemd/system/irrigacion.service

# Recarga systemd
sudo systemctl daemon-reload
```

### Paso 3: Habilita el servicio
```bash
# Para que inicie automáticamente al arrancar
sudo systemctl enable irrigacion.service
```

### Paso 4: Inicia el servicio
```bash
# Inicia ahora
sudo systemctl start irrigacion.service

# Verifica que está corriendo
sudo systemctl status irrigacion.service
```

✅ Deberías ver: `active (running)`

### Paso 5: Verifica que funciona
```bash
# Ver los logs en tiempo real
journalctl -u irrigacion -f

# O en otra terminal
sudo python3 scripts/test_zones_quick.py
```

---

## Contenido del archivo `irrigacion.service`

```ini
[Unit]
Description=Sistema de Riego Inteligente
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/alexdev/Documents/irrigacion
ExecStart=/usr/bin/python3 /home/alexdev/Documents/irrigacion/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Nota**: Si tu usuario no es `pi`, cambia `User=pi` por tu usuario.

---

## Comandos Útiles

```bash
# Ver estado
sudo systemctl status irrigacion.service

# Iniciar
sudo systemctl start irrigacion.service

# Detener
sudo systemctl stop irrigacion.service

# Reiniciar
sudo systemctl restart irrigacion.service

# Ver logs
journalctl -u irrigacion -f

# Ver últimas líneas
journalctl -u irrigacion -n 50

# Habilitar en inicio
sudo systemctl enable irrigacion.service

# Deshabilitar en inicio
sudo systemctl disable irrigacion.service
```

---

## Si el Servicio Falla

### Verifica el archivo
```bash
systemctl cat irrigacion.service
```

### Valida la sintaxis
```bash
sudo systemd-analyze verify irrigacion.service
```

### Ve el error completo
```bash
journalctl -u irrigacion -n 100
```

### Reinicia manualmente para debuggear
```bash
cd /home/alexdev/Documents/irrigacion
python3 run.py
```

---

## Estado Final Esperado

Después de completar todos los pasos:

```bash
$ sudo systemctl status irrigacion.service
● irrigacion.service - Sistema de Riego Inteligente
     Loaded: loaded (/etc/systemd/system/irrigacion.service; enabled; vendor preset: disabled)
     Active: active (running) since Mar 25 12:34:56 2026
   Main PID: 1234 (python3)
      Tasks: 10 (limit: 4915)
     Memory: 45.2M
     CGroup: /system.slice/irrigacion.service
             └─1234 /usr/bin/python3 /home/alexdev/Documents/irrigacion/run.py
```

✅ **¡El servicio está configurado y ejecutándose!**

---

**Tiempo estimado**: 5 minutos
**Dificultad**: Baja

