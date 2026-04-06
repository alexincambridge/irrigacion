#!/usr/bin/env python3
"""
Test rápido para verificar que Telegram funciona.
Uso: python3 scripts/test_telegram.py
"""

import urllib.request
import urllib.parse
import json
import sys
import os
import importlib.util

# Cargar config.py directamente sin importar todo el paquete app
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "config.py")
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

TELEGRAM_BOT_TOKEN = getattr(config, "TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = getattr(config, "TELEGRAM_CHAT_ID", "")
NOTIFICATIONS_ENABLED = getattr(config, "NOTIFICATIONS_ENABLED", False)

print("=" * 50)
print("  TEST DE NOTIFICACIONES TELEGRAM")
print("=" * 50)
print()
print(f"  NOTIFICATIONS_ENABLED: {NOTIFICATIONS_ENABLED}")
print(f"  TELEGRAM_BOT_TOKEN:    {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}" if len(TELEGRAM_BOT_TOKEN) > 15 else f"  TELEGRAM_BOT_TOKEN:    {TELEGRAM_BOT_TOKEN}")
print(f"  TELEGRAM_CHAT_ID:      {TELEGRAM_CHAT_ID}")
print()

if TELEGRAM_BOT_TOKEN == "PEGA_TU_NUEVO_TOKEN_AQUI" or not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: El token no está configurado!")
    print("   Edita app/config.py y pega tu token de @BotFather")
    print()
    print("   Pasos:")
    print("   1. Abre Telegram → @BotFather")
    print("   2. Envía /mybots → selecciona tu bot → API Token")
    print("   3. Copia el token y pégalo en app/config.py línea 52")
    sys.exit(1)

if not NOTIFICATIONS_ENABLED:
    print("⚠️  NOTIFICATIONS_ENABLED está en False")
    sys.exit(1)

print("📡 Enviando mensaje de prueba...")
print()

try:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🧪 <b>Test de Notificaciones</b>\n━━━━━━━━━━━━━━━\n✅ Telegram funciona correctamente\n💧 Sistema de Riego Inteligente",
        "parse_mode": "HTML"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req, timeout=10)
    result = json.loads(response.read().decode("utf-8"))

    if result.get("ok"):
        print("✅ ¡MENSAJE ENVIADO CORRECTAMENTE!")
        print("   Revisa tu Telegram, debería haber llegado.")
    else:
        print(f"❌ Telegram respondió con error:")
        print(f"   {result}")

except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8")
    error_data = json.loads(error_body)
    error_code = error_data.get("error_code", "?")
    description = error_data.get("description", "Sin descripción")

    print(f"❌ ERROR HTTP {e.code}:")
    print(f"   Código Telegram: {error_code}")
    print(f"   Descripción: {description}")
    print()

    if error_code == 401:
        print("   → El TOKEN es inválido o fue revocado.")
        print("   → Ve a @BotFather y genera uno nuevo con /revoke + /newbot")
    elif error_code == 400 and "chat not found" in description.lower():
        print("   → El CHAT_ID es incorrecto.")
        print("   → Asegúrate de haber enviado /start a tu bot primero")
        print(f"   → Luego visita: https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates")
        print("   → Busca el campo 'chat': {'id': XXXXX}")
    elif error_code == 403:
        print("   → El bot fue bloqueado por el usuario.")
        print("   → Desbloquea el bot en Telegram y envía /start")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("   Verifica tu conexión a internet")

print()

