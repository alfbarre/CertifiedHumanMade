import hashlib
import os
import json
import time
import atexit
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def getFileHash(filePath: str):
    with open(filePath, 'rb') as file:
        fileData: bytes = file.read()
        hashObject: hashlib._Hash = hashlib.sha256(fileData)
        return hashObject.hexdigest()


def generateLogEntry(filePath: str) -> dict:
    # Basic file info
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Time log was started
    fileSizeBytes: int = os.path.getsize(filePath)
    fileName: str = os.path.basename(filePath)
    fileHash: str = getFileHash(filePath)

    # File creation time
    createdTime = os.path.getctime(filePath)
    createdAt: str = datetime.fromtimestamp(createdTime).strftime("%Y-%m-%d %H:%M:%S")

    # Last modified time
    modifiedTime = os.path.getmtime(filePath)
    modifiedAt: str = datetime.fromtimestamp(modifiedTime).strftime("%Y-%m-%d %H:%M:%S")

    logEntry: dict = {
        "timestamp": timestamp,
        "fileName": fileName,
        "filePath": filePath,
        "fileSizeBytes": fileSizeBytes,
        "sha256": fileHash,
        "fileCreatedAt": createdAt,
        "fileModifiedAt": modifiedAt
    }

    return logEntry


def saveLogToJsonFile(logData: dict, outputPath: str):
    with open(outputPath, 'w') as jsonFile:
        json.dump(logData, jsonFile, indent=4)
    print("Log saved to " + outputPath)
    print("")


# Watchdog Handler Class
class ALSFileChangeHandler(FileSystemEventHandler):

    def __init__(self, sessionTracker):
        self.sessionTracker = sessionTracker
        self.lastHandled = {}
        self.cooldownSeconds = 2  # Prevent duplicate watchdog

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".als"):
            now = time.time()
            lastTime = self.lastHandled.get(event.src_path, 0)

            if now - lastTime >= self.cooldownSeconds:
                self.lastHandled[event.src_path] = now

                print("[WATCHDOG] Detected Change: " + event.src_path)
                log = generateLogEntry(event.src_path)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                outputFilePath = event.src_path + f"_log_{timestamp}.json"
                saveLogToJsonFile(log, outputFilePath)

                self.sessionTracker.recordEdit()


class SessionTracker:
    def __init__(self, idleTimeOut=300):  # 5 minutes
        self.sessionActive = False
        self.sessionStart = None
        self.lastEdit = None
        self.editCount = 0
        self.idleTimeOut = idleTimeOut

    def recordEdit(self):
        now = datetime.now()
        if not self.sessionActive:
            self.sessionStart = now
            self.editCount = 0
            print("[SESSION] Started at:", self.sessionStart.strftime("%Y-%m-%d %H:%M:%S"))
            self.sessionActive = True

        self.lastEdit = now
        self.editCount += 1

    def checkIdle(self):
        if self.sessionActive and self.lastEdit:
            elapsed = (datetime.now() - self.lastEdit).total_seconds()
            if elapsed > self.idleTimeOut:
                self.endSession()

    def cleanup(self):
        self.checkIdle()
        if self.sessionActive:
            self.endSession()

    def endSession(self):
        self.sessionActive = False
        sessionEnd = datetime.now()
        duration = (sessionEnd - self.sessionStart).total_seconds()

        sessionLog: dict = {
            "sessionStart": self.sessionStart.strftime("%Y-%m-%d %H:%M:%S"),
            "sessionEnd": sessionEnd.strftime("%Y-%m-%d %H:%M:%S"),
            "durationSeconds": int(duration),
            "durationReadable": str(sessionEnd - self.sessionStart),
            "editCount": self.editCount
        }

        fileName = f"session_log_{sessionEnd.strftime('%Y%m%d_%H%M%S')}.json"
        saveLogToJsonFile(sessionLog, fileName)
        print("[SESSION] Ended. Duration:", sessionLog["durationReadable"])
        print("")


if __name__ == '__main__':
    # Test Path: C:\Users\firef\Documents\Backup\Ableton Projects\Twelve\Twelve Project
    folderToWatch: str = input("Enter the path to your Ableton project folder: ")
    sessionTracker = SessionTracker(idleTimeOut=300)
    eventHandler = ALSFileChangeHandler(sessionTracker)
    observer = Observer()
    atexit.register(sessionTracker.cleanup)

    observer.schedule(eventHandler, path=folderToWatch, recursive=False)
    observer.start()
    print("[WATCHDOG] Started: watching for changes in: " + folderToWatch)
    print("")

    try:
        while True:
            sessionTracker.checkIdle()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[WATCHDOG] stopping...")
    observer.join()
