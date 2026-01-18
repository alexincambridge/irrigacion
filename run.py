from app import create_app
from app.scheduler import scheduler_loop
import threading

app = create_app()

threading.Thread(
    target=scheduler_loop,
    daemon=True
).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
