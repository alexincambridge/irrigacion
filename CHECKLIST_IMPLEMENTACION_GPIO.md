# ✅ CHECKLIST DE IMPLEMENTACIÓN

## Pre-Implementación
- [ ] Backup de la base de datos
- [ ] Apagar todos los riegos manuales
- [ ] Desactivar riegos programados (si es necesario)

## Archivos a Verificar
- [ ] `app/config.py` - Verificar `HARDWARE_MODE = 'GPIO'`
- [ ] `app/hardware_manager.py` - Archivo nuevo, debe existir
- [ ] `app/hardware.py` - Debe estar actualizado
- [ ] `app/__init__.py` - Importación actualizada
- [ ] `app/routes.py` - Todas las importaciones actualizadas
- [ ] `app/scheduler.py` - Importación actualizada
- [ ] `app/irrigation.py` - Importación actualizada

## Validación de Sintaxis
```bash
cd /Users/alexg/Sites/irrigacion
python3 -m py_compile app/hardware_manager.py app/hardware.py
```
- [ ] Sin errores de compilación

## Test de GPIOs
```bash
# Opción 1: Test Rápido
sudo python3 scripts/test_zones_quick.py

# Opción 2: Test Completo
sudo python3 scripts/diagnose_gpio.py
```
- [ ] Zona 1 (GPIO 23): OK
- [ ] Zona 2 (GPIO 24): OK
- [ ] Zona 3 (GPIO 25): OK
- [ ] Zona 4 (GPIO 27): OK
- [ ] Bomba (GPIO 17): OK

## Reinicio de Aplicación
```bash
# Si usas systemd
sudo systemctl restart irrigacion

# O si ejecutas manualmente
python3 run.py
```
- [ ] Aplicación inicia sin errores
- [ ] Logs muestran inicialización correcta

## Test en Interfaz Web
- [ ] Navega a `/irrigation`
- [ ] Abre "Control Manual de Zonas"
- [ ] Test Zona 1:
  - [ ] Botón "Iniciar" activa el relé
  - [ ] LED en el relé se enciende
  - [ ] Botón cambia a "Detener"
  - [ ] Botón "Detener" apaga el relé
- [ ] Test Zona 2:
  - [ ] Botón "Iniciar" activa el relé
  - [ ] LED en el relé se enciende
  - [ ] Botón cambia a "Detener"
  - [ ] Botón "Detener" apaga el relé
- [ ] Test Zona 3:
  - [ ] Botón "Iniciar" activa el relé
  - [ ] LED en el relé se enciende
  - [ ] Botón cambia a "Detener"
  - [ ] Botón "Detener" apaga el relé
- [ ] Test Zona 4:
  - [ ] Botón "Iniciar" activa el relé
  - [ ] LED en el relé se enciende
  - [ ] Botón cambia a "Detener"
  - [ ] Botón "Detener" apaga el relé

## Test de Riegos Programados
- [ ] Crear nuevo riego programado para zona 1
- [ ] Crear nuevo riego programado para zona 2
- [ ] Crear nuevo riego programado para zona 3
- [ ] Crear nuevo riego programado para zona 4
- [ ] Verificar que se activan en el momento programado
- [ ] Verificar que se desactivan cuando el tiempo expira

## Test de Riegos Manuales
- [ ] Iniciar riego manual en zona 1
- [ ] Iniciar riego manual en zona 2 (mientras zona 1 está activa)
- [ ] Verificar que ambas zonas funcionan simultáneamente
- [ ] Detener zona 1
- [ ] Detener zona 2

## Test de Botón de Emergencia
- [ ] Activar varias zonas
- [ ] Hacer clic en "Detener Todo"
- [ ] Verificar que todas las zonas se desactivan inmediatamente

## Test de Bomba (Fertilización)
- [ ] Ir a página de Fertilización
- [ ] Activar la bomba
- [ ] Verificar que el GPIO 17 se activa
- [ ] Deactivar la bomba
- [ ] Verificar que el GPIO 17 se desactiva

## Test de Logs
```bash
# Ver los últimos logs
journalctl -u irrigacion -n 50 -f

# O si ejecutas manualmente, busca mensajes como:
# [HW] ✅ Zona X ON (GPIO XX)
# [HW] ✅ Zona X OFF (GPIO XX)
```
- [ ] Los logs muestran las activaciones/desactivaciones
- [ ] No hay errores de GPIO

## Post-Implementación
- [ ] Documentación actualizada
- [ ] Equipo notificado de los cambios
- [ ] Monitoreo de la aplicación durante 24 horas
- [ ] Confirmar estabilidad

## Rollback (Si es Necesario)
Si algo falla:
```bash
# Revert a hardware.py original
git checkout app/config.py app/hardware.py

# O restaurar desde backup
cp backup/config.py app/
cp backup/hardware.py app/

# Reiniciar
sudo systemctl restart irrigacion
```
- [ ] Sistema vuelve a su estado anterior

---

**Fecha**: Marzo 2026
**Implementador**: _____________________
**Firma**: _____________________

