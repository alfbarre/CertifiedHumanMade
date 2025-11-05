import time
from datetime import datetime
from watchdog.events import FileSystemEventHandler
from fileLogger import generateLogEntry, saveLogToJsonFile

class ALSFileChangeHandler(FileSystemEventHandler):
    def __init__(self, sessionTracker):
        self.sessionTracker = sessionTracker
        self.lastHandled = {}
        self.cooldownSeconds = 2

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".als"):
            now = time.time()
            lastTime = self.lastHandled.get(event.src_path, 0)

            if now - lastTime >= self.cooldownSeconds:
                self.lastHandled[event.src_path] = now
                print("[WATCHDOG] Detected Change:", event.src_path)

                log = generateLogEntry(event.src_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                outputPath = event.src_path + f"_log_{timestamp}.json"
                saveLogToJsonFile(log, outputPath)

                self.sessionTracker.recordEdit()
