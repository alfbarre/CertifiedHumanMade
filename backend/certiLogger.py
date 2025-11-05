import time
import atexit
from watchdog.observers import Observer
from alsWatcher import ALSFileChangeHandler
from sessionTracker import SessionTracker

# Test Path: C:\Users\firef\Documents\Backup\Ableton Projects\Twelve\Twelve Project

# Main

if __name__ == '__main__':
    folderToWatch = input("Enter the path to your Ableton project folder: ")
    sessionTracker = SessionTracker(idleTimeOut=300)
    eventHandler = ALSFileChangeHandler(sessionTracker)
    observer = Observer()
    atexit.register(sessionTracker.cleanup)

    observer.schedule(eventHandler, path=folderToWatch, recursive=False)
    observer.start()
    print("[WATCHDOG] Started: watching for changes in:", folderToWatch)
    print("")

    try:
        while True:
            sessionTracker.checkIdle()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[WATCHDOG] Stopping...")
    observer.join()
