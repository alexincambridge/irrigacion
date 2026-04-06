#!/usr/bin/env python3
"""
Obtener el chat_id correcto de Telegram.
1. Envia /start a tu bot en Telegram
2. Ejecuta: python3 scripts/get_telegram_chatid.py
"""
import urllib.request, json, sys, os, importlib.util

config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "config.py")
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
TOKEN = getattr(config, "TELEGRAM_BOT_TOKEN", "")

if not TOKEN or TOKEN == "PEGA_TU_NUEVO_TOKEN_AQUI":
    print("Token no configurado en app/config.py")
    sys.exit(1)

print("Consultando getUpdates...")
try:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = urllib.request.urlopen(urllib.request.Request(url), timeout=10)
    data = json.loads(response.read().decode("utf-8"))
    results = data.get("result", [])
    if not results:
        print("No hay mensajes. Envia /start al bot primero y vuelve a ejecutar.")
        sys.exit(1)
    chats = {}
    for u in results:
        chat = u.get("message", {}).get("chat", {})
        cid = chat.get("id")
        if cid:
            chats[cid] = chat.get("first_name", "")
    for cid, name in chats.items():
        print(f"  Chat ID: {cid}  ->  {name}")
    if len(chats) == 1:
        print(f"\nPon esto en app/config.py:\n   TELEGRAM_CHAT_ID = \"{list(chats.keys())[0]}\"")
except Exception as e:
    print(f"Error: {e}")

