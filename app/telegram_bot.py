import time
import urllib.request
import urllib.parse
import urllib.error
import json
import logging
import threading
from datetime import datetime, timedelta
import sqlite3
import os

logger = logging.getLogger(__name__)

def _get_config():
    try:
        from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NOTIFICATIONS_ENABLED
        return TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NOTIFICATIONS_ENABLED
    except (ImportError, AttributeError):
        return None, None, False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")

class TelegramBotListener:
    def __init__(self):
        self.offset = None
        self.running = False
        self.thread = None

    def start(self):
        token, chat_id, enabled = _get_config()
        if not enabled or not token:
            return
        if self.running:
            return

        logger.info("[Telegram] Iniciando bot listener...")
        self.running = True
        self.thread = threading.Thread(target=self.poll, daemon=True)
        self.thread.start()

    def poll(self):
        while self.running:
            try:
                token, chat_id, enabled = _get_config()
                if not enabled or not token:
                    time.sleep(10)
                    continue

                url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {"timeout": 30}
                if self.offset:
                    params["offset"] = self.offset

                query_string = urllib.parse.urlencode(params)
                req_url = f"{url}?{query_string}"

                req = urllib.request.Request(req_url)
                response = urllib.request.urlopen(req, timeout=40)
                data = json.loads(response.read().decode("utf-8"))

                if data.get("ok"):
                    for update in data.get("result", []):
                        self.offset = update["update_id"] + 1
                        message = update.get("message")
                        if message and message.get("text"):
                            self.process_message(message, token, chat_id)
            except urllib.error.URLError as e:
                # Expected timeout or network fail
                time.sleep(5)
            except Exception as e:
                logger.error(f"[Telegram] Error polling: {e}")
                time.sleep(5)

    def process_message(self, message, token, authorized_chat_id):
        text = message.get("text", "").lower().strip()
        sender_chat_id = str(message.get("chat", {}).get("id"))

        if str(authorized_chat_id) != "0" and sender_chat_id != str(authorized_chat_id):
            return

        if text.startswith("/riego"):
            parts = text.split()
            if len(parts) == 3:
                try:
                    zona = int(parts[1])
                    duracion_min = int(parts[2])
                    if zona not in [1, 2, 3, 4] or duracion_min <= 0 or duracion_min > 120:
                        self.send_message(token, sender_chat_id, "❌ Zona inválida (1-4) o duración (1-120 min).")
                        return

                    self.start_irrigation(zona, duracion_min)
                    self.send_message(token, sender_chat_id, f"✅ Riego programado en zona {zona} por {duracion_min} minutos vía Telegram.")
                except ValueError:
                    self.send_message(token, sender_chat_id, "❌ Formato incorrecto. Uso: /riego <zona> <minutos>")
                except Exception as e:
                    logger.error(f"[Telegram] Error al procesar riego: {e}")
                    self.send_message(token, sender_chat_id, f"❌ Error al iniciar riego.")
            else:
                self.send_message(token, sender_chat_id, "❌ Formato incorrecto. Uso: /riego <zona> <minutos>\nEjemplo: /riego 1 30")
        elif text == "/stop":
            try:
                from app.hardware_manager import all_off
                all_off()

                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("UPDATE irrigation_log SET end_time = ?, status = 'cancelado' WHERE end_time IS NULL", (now_str,))
                cur.execute("UPDATE irrigation_schedule SET enabled = 0, status = 'cancelado' WHERE enabled = 1")
                conn.commit()
                conn.close()
                self.send_message(token, sender_chat_id, "🚨 Parada de emergencia ejecutada.")
            except Exception as e:
                self.send_message(token, sender_chat_id, f"❌ Error en parada: {e}")
        elif text == "/help":
            help_msg = (
                "🤖 <b>Bot Riego Inteligente</b>\n\n"
                "Instrucciones:\n"
                "💧 /riego &lt;zona&gt; &lt;minutos&gt;: Inicia un riego en la zona indicada por el tiempo especificado.\n"
                "🛑 /stop: Detener todo inmediatamente."
            )
            self.send_message(token, sender_chat_id, help_msg)

    def start_irrigation(self, sector, duration_minutes):
        now = datetime.now()
        end = now + timedelta(minutes=duration_minutes)

        today = now.strftime("%Y-%m-%d")
        start_time = now.strftime("%H:%M")
        end_time = end.strftime("%H:%M")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Priority mapping
        priority_map = {4: 1, 1: 2, 2: 3, 3: 4}
        priority = priority_map.get(sector, 0)

        cur.execute("""
            INSERT INTO irrigation_schedule 
            (sector, date, start_time, end_time, duration, duration_minutes, status, priority, 
             repeat_days, repeat_enabled, origin, enabled)
            VALUES (?, ?, ?, ?, ?, ?, 'en espera', ?, '', 0, 'telegram', 1)
        """, (sector, today, start_time, end_time, duration_minutes, duration_minutes, priority))

        conn.commit()
        conn.close()

    def send_message(self, token, chat_id, text):
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logger.error(f"[Telegram] Error enviando mensaje: {e}")

bot_listener = TelegramBotListener()
