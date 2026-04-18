# 🚀 COMANDOS RÁPIDOS - Instalar Servicio

## En tu RPi, ejecuta esto EN ORDEN:

```bash
# 1. Ve al directorio
cd /home/alexdev/Documents/irrigacion

# 2. Instala el servicio
sudo cp irrigacion.service /etc/systemd/system/irrigacion.service

# 3. Dale permisos
sudo chmod 644 /etc/systemd/system/irrigacion.service

# 4. Recarga systemd
sudo systemctl daemon-reload

# 5. Habilita el servicio (opcional, pero recomendado)
sudo systemctl enable irrigacion.service

# 6. Inicia el servicio
sudo systemctl start irrigacion.service

# 7. Verifica que está corriendo
sudo systemctl status irrigacion.service
```

✅ Debería mostrar: `active (running)`

## Ahora puedes:

```bash
# Reiniciar la aplicación
sudo systemctl restart irrigacion.service

# Ver los logs
journalctl -u irrigacion -f

# Probar que funciona
sudo python3 scripts/test_zones_quick.py
```

---

## Si necesitas cambiar algo

**Si tu usuario NO es `pi`:**
```bash
# Edita el archivo
sudo nano /etc/systemd/system/irrigacion.service

# Cambia la línea:
# User=pi
# Por:
# User=tu-usuario

# Guarda (Ctrl+O, Enter, Ctrl+X)
# Y reinicia:
sudo systemctl daemon-reload
sudo systemctl restart irrigacion.service
```

---

**¡Listo!** El servicio está instalado y funcionando. ✅

