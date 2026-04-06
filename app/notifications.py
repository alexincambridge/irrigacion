"""
Módulo de notificaciones Telegram para el sistema de riego.
Envía mensajes al finalizar riegos, cancelaciones y emergencias.
Los mensajes se envían en threads separados para no bloquear el sistema.
"""

import threading
import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

ZONE_NAMES = {
    1: "Jardín",
    2: "Huerta",
    3: "Césped",
    4: "Árboles"
}


def _get_config():
    """Obtener configuración de Telegram de forma segura."""
    try:
        from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NOTIFICATIONS_ENABLED
        return TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NOTIFICATIONS_ENABLED
    except (ImportError, AttributeError):
        return None, None, False


def send_telegram(message):
    """Enviar mensaje por Telegram en un thread separado (no bloqueante)."""
    def _send():
        try:
            token, chat_id, enabled = _get_config()
            if not enabled or not token or not chat_id:
                logger.debug("[Telegram] Notificaciones desactivadas o sin configurar")
                return

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read().decode("utf-8"))

            if result.get("ok"):
                logger.info("[Telegram] ✅ Mensaje enviado correctamente")
            else:
                logger.warning(f"[Telegram] ⚠️ Respuesta inesperada: {result}")

        except Exception as e:
            logger.error(f"[Telegram] ❌ Error enviando mensaje: {e}")

    threading.Thread(target=_send, daemon=True).start()


# ========================================
# NOTIFICACIONES DE RIEGO
# ========================================

def notify_irrigation_completed(sector, start_time, end_time, duration_minutes, irrigation_type="programado"):
    """Notificar cuando un ciclo de riego termina correctamente."""
    zone_name = ZONE_NAMES.get(sector, f"Zona {sector}")
    duration_str = f"{duration_minutes} min" if duration_minutes else "N/A"
    type_icon = "🕐 Programado" if irrigation_type == "programado" else "✋ Manual"

    message = (
        f"✅ <b>Riego Finalizado</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌱 Zona: <b>{zone_name}</b> (Sector {sector})\n"
        f"📋 Tipo: {type_icon}\n"
        f"🕐 Inicio: {start_time}\n"
        f"🕑 Fin: {end_time}\n"
        f"⏱ Duración: {duration_str}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💧 Sistema de Riego Inteligente"
    )
    send_telegram(message)


def notify_irrigation_started(sector, irrigation_type="programado"):
    """Notificar cuando un riego arranca."""
    zone_name = ZONE_NAMES.get(sector, f"Zona {sector}")
    type_icon = "🕐 Programado" if irrigation_type == "programado" else "✋ Manual"
    now = datetime.now().strftime("%H:%M:%S")

    message = (
        f"▶️ <b>Riego Iniciado</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌱 Zona: <b>{zone_name}</b> (Sector {sector})\n"
        f"📋 Tipo: {type_icon}\n"
        f"🕐 Hora: {now}\n"
        f"━━━━━━━━━━━━━━━"
    )
    send_telegram(message)


def notify_irrigation_cancelled(sector, reason="Cancelado por usuario"):
    """Notificar cuando un riego es cancelado."""
    zone_name = ZONE_NAMES.get(sector, f"Zona {sector}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"⚠️ <b>Riego Cancelado</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌱 Zona: <b>{zone_name}</b> (Sector {sector})\n"
        f"📋 Motivo: {reason}\n"
        f"🕐 Hora: {now}\n"
        f"━━━━━━━━━━━━━━━"
    )
    send_telegram(message)


def notify_emergency_stop():
    """Notificar parada de emergencia."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"🚨 <b>PARADA DE EMERGENCIA</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⛔ Todas las zonas han sido apagadas\n"
        f"⛔ Todos los riegos programados cancelados\n"
        f"🕐 Hora: {now}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ Revise el sistema inmediatamente"
    )
    send_telegram(message)


def notify_daily_summary(total_irrigations, completed, cancelled, total_minutes):
    """Enviar resumen diario de riegos."""
    today = datetime.now().strftime("%Y-%m-%d")

    message = (
        f"📊 <b>Resumen Diario de Riego</b>\n"
        f"📅 {today}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📋 Total riegos: {total_irrigations}\n"
        f"✅ Completados: {completed}\n"
        f"❌ Cancelados: {cancelled}\n"
        f"⏱ Tiempo total: {total_minutes} min\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💧 Sistema de Riego Inteligente"
    )
    send_telegram(message)

