from flask import Flask, request, jsonify
from flask_cors import CORS
from sessionTracker import SessionTracker
from alsWatcher import ALSFileChangeHandler
from watchdog.observers import Observer
import atexit
import time
import threading

app = Flask(__name__)
CORS(app)

observer = None
sessionTracker = None

def startMonitoring(folderPath: str):
    global observer, sessionTracker
    if observer:
        return

    sessionTracker = SessionTracker(idleTimeOut=300)
    eventHandler = ALSFileChangeHandler(sessionTracker)
    observer = Observer()
    observer.schedule(eventHandler, path=folderPath, recursive=False)
    observer.start()
    print("[WATCHDOG] Started:", folderPath)

    def idleChecker():
        while observer:
            sessionTracker.checkIdle()
            time.sleep(1)

    threading.Thread(target=idleChecker, daemon=True).start()
    atexit.register(sessionTracker.cleanup)

def stopMonitoring():
    global observer
    if observer:
        observer.stop()
        observer.join()
        print("[WATCHDOG] Stopped.")
        observer = None

@app.route("/start", methods=["POST"])
def start():
    folder = request.json.get("folderPath")
    if not folder:
        return jsonify({"error": "folderPath is required"}), 400

    startMonitoring(folder)
    return jsonify({"status": "started", "folder": folder})

@app.route("/stop", methods=["POST"])
def stop():
    stopMonitoring()
    return jsonify({"status": "stopped"})

@app.route("/status", methods=["GET"])
def status():
    if not sessionTracker:
        return jsonify({"active": False})
    return jsonify({
        "active": sessionTracker.sessionActive,
        "editCount": sessionTracker.editCount,
        "lastEdit": str(sessionTracker.lastEdit)
    })

if __name__ == "__main__":
    app.run(debug=True)
