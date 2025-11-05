import hashlib
import os
import json
from datetime import datetime

def getFileHash(filePath: str):
    with open(filePath, 'rb') as file:
        fileData = file.read()
        return hashlib.sha256(fileData).hexdigest()

def generateLogEntry(filePath: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fileSizeBytes = os.path.getsize(filePath)
    fileName = os.path.basename(filePath)
    fileHash = getFileHash(filePath)
    createdAt = datetime.fromtimestamp(os.path.getctime(filePath)).strftime("%Y-%m-%d %H:%M:%S")
    modifiedAt = datetime.fromtimestamp(os.path.getmtime(filePath)).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "timestamp": timestamp,
        "fileName": fileName,
        "filePath": filePath,
        "fileSizeBytes": fileSizeBytes,
        "sha256": fileHash,
        "fileCreatedAt": createdAt,
        "fileModifiedAt": modifiedAt
    }

def saveLogToJsonFile(logData, outputPath):
    with open(outputPath, 'w') as jsonFile:
        json.dump(logData, jsonFile, indent=4)
    print("Log saved to", outputPath)
    print("")
