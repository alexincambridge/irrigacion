from app import create_app
from app.scheduler import scheduler_loop
from app.telegram_bot import bot_listener
import threading
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")

app = create_app()

threading.Thread(
    target=scheduler_loop,
    daemon=True
).start()

bot_listener.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
