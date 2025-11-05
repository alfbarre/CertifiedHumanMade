from datetime import datetime
from fileLogger import saveLogToJsonFile

class SessionTracker:
    def __init__(self, idleTimeOut=300):
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

        sessionLog = {
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
