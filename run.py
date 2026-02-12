from app import create_app
from app.scheduler import scheduler_loop
import threading
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")

app = create_app()

threading.Thread(
    target=scheduler_loop,
    daemon=True
).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
