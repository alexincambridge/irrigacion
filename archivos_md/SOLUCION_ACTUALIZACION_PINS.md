# 🔧 SOLUCIÓN - Actualización de Pines GPIO

## El Problema
Los pines de los relés han cambiado, pero la aplicación sigue usando los antiguos.
- **Nuevos pines**: 16, 23, 24, 26
- **Problema**: Los pines 16 y 26 no funcionan desde la app porque no están configurados.

## La Solución
He actualizado todos los archivos necesarios para que usen la nueva configuración de pines.

### Archivos Modificados

1.  **`app/hardware.py`**:
    - Se cambió la configuración de `ZONE_PINS` para usar los nuevos GPIOs.
    - Este es el archivo principal que controla el hardware.

2.  **`app/config.py`**:
    - Se actualizó el diccionario `PERIPHERALS` para que la página de "Sistema" (health check) muestre los pines correctos.

3.  **`scripts/diagnose_gpio.py`**:
    - Se actualizó `ZONE_PINS` en el script de diagnóstico para que puedas probar los nuevos pines directamente.

## Pasos para Aplicar la Solución

### 1. Actualiza los Archivos
Asegúrate de que los cambios se han aplicado en tu Raspberry Pi. Si usas `git`, haz un `git pull`.

### 2. Reinicia la Aplicación
Para que los cambios en `hardware.py` y `config.py` tengan efecto, reinicia el servicio:
```bash
sudo systemctl restart irrigacion.service
```

### 3. Verifica que Funciona

#### Opción A: Desde la Interfaz Web (Recomendado)
1.  Abre la página de Riego.
2.  Prueba a activar manualmente cada una de las 4 zonas.
3.  **Todas deberían funcionar ahora**, incluyendo las conectadas a los pines 16 y 26.

#### Opción B: Usando el Script de Diagnóstico
Si algo sigue sin funcionar, este script te dirá exactamente qué pin está fallando.
```bash
cd /home/alexdev/Documents/irrigacion
sudo python3 scripts/diagnose_gpio.py
```
**Resultado esperado**:
```
✅ TODOS LOS GPIO FUNCIONAN CORRECTAMENTE
```

## Resumen de la Nueva Configuración

| Zona | Nombre | GPIO Antiguo | GPIO Nuevo |
| :--- | :--- | :--- | :--- |
| 1 | Jardín | 23 | **16** |
| 2 | Huerta | 24 | **23** |
| 3 | Césped | 25 | **24** |
| 4 | Árboles | 27 | **26** |

---

**Estado**: ✅ **COMPLETADO**. Los archivos han sido actualizados. Solo necesitas reiniciar la aplicación para que los cambios surtan efecto.

