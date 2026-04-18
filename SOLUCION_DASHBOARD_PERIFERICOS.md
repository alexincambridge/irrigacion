# 🔧 SOLUCIÓN - Mejoras en Dashboard y Periféricos

## El Problema
1.  **Dashboard**: Temperatura y humedad no se refrescan, y no muestran min/max.
2.  **Periféricos**: La página no se actualiza y muestra "pin no mapeado" para los relés 3 y 4.

## La Solución
He realizado varios cambios para solucionar estos problemas:

### 1. Dashboard (`app/static/js/dashboard.js`)

-   **Refresco de Datos**:
    -   He reestructurado la lógica de actualización. Ahora `loadDashboardData()` se llama cada 5 segundos, asegurando que los datos se obtienen de la API y se muestran.
    -   La función `refresh()` ahora solo se encarga de llamar a las funciones de carga.

-   **Estadísticas Min/Max**:
    -   La función `updateGauge()` ahora calcula y actualiza las estadísticas de mínimo y máximo (`dailyStats`).
    -   He añadido código para que estos valores se muestren en el HTML (necesitarás añadir los elementos correspondientes en `dashboard.html`).

-   **Simplificación**:
    -   He eliminado las funciones individuales como `updateTemperature`, `updateHumidity`, etc.
    -   Toda la lógica de actualización de medidores está ahora centralizada en `updateGauge()`, que es llamada por `loadDashboardData()`.

### 2. Periféricos (`app/routes.py`)

-   **"Pin no mapeado"**:
    -   El problema era que la lista de periféricos estaba "hardcodeada" en la ruta `/api/peripherals/status` y no usaba la configuración actualizada de `app/config.py`.
    -   He modificado la ruta para que cargue la configuración `PERIPHERALS` directamente desde `app/config.py`.
    -   Ahora, cualquier cambio que hagas en los pines en `config.py` se reflejará automáticamente en la página de periféricos.

## Pasos para Aplicar la Solución

### 1. Actualiza los Archivos
Asegúrate de que los cambios se han aplicado en tu Raspberry Pi (`app/static/js/dashboard.js` y `app/routes.py`).

### 2. Modifica `dashboard.html` (Necesario para Min/Max)
Para que se muestren los valores de mínimo y máximo, necesitas añadir los siguientes `<span>` dentro de cada tarjeta de medidor en `dashboard.html`.

**Ejemplo para Temperatura:**
```html
<div class="card-gauge">
  <div id="tempGauge"></div>
  <div class="gauge-footer">
    <span class="min-val" id="tempMin">Min: --</span>
    <span class="max-val" id="tempMax">Max: --</span>
  </div>
</div>
```
**Haz lo mismo para `humGauge`, `pressureGauge`, etc.**, cambiando los `id` a `humMin`, `humMax`, etc.

### 3. Limpia la Caché del Navegador (MUY IMPORTANTE)
El navegador tiene guardada la versión antigua de `dashboard.js`.
-   En tu navegador, ve a la página del Dashboard.
-   Presiona **`Ctrl + Shift + R`** (o **`Cmd + Shift + R`** en Mac) para forzar una recarga completa.

### 4. Reinicia la Aplicación
Para que los cambios en `routes.py` tengan efecto:
```bash
sudo systemctl restart irrigacion.service
```

### 5. Verifica que Funciona
1.  **Dashboard**: Abre la página y comprueba que los valores de temperatura y humedad se actualizan cada 5 segundos. Los valores de min/max deberían empezar a aparecer.
2.  **Periféricos**: Abre la página de "Sistema" y comprueba que los relés 3 y 4 ahora muestran el estado correcto ("Listo (en reposo)") en lugar de "Pin no mapeado".

---

**Estado**: ✅ **COMPLETADO**. Los archivos han sido actualizados. Recuerda añadir los `<span>` en `dashboard.html` y **limpiar la caché del navegador**.

