from app import create_app
from app.scheduler import scheduler_loop
import threading

app = create_app()
threading.Thread(target=scheduler_loop, daemon=True).start()

app.run(host="0.0.0.0", port=5000)
