import threading
from app import app as flask_app
from bot import main

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()

    # now blocking call
    main()
