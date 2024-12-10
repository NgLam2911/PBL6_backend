from .class_pattern import Singleton
from .notificator import Notificator

import uuid as uuid_generator
import base64
import time

def generateToken():
    return base64.b64encode(generateUUID().encode()).decode().replace('-', '')

def generateUUID():
    return str(uuid_generator.uuid4())

def generateCameraId():
    return generateUUID()[:8]

def generateLinkingCode():
    return generateUUID()[:6]

def hms2unix(hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    return hours * 3600 + minutes * 60 + seconds

def unixNow() -> int:
    return int(time.time())

def unix2dmyhms(unix: int) -> str:
    # GMT+7
    return time.strftime(r"%d-%m-%Y %H:%M:%S", time.gmtime(unix + 25200))

def createThumbnail(video_path: str, thumbnail_path: str):
    import cv2
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
    success, image = cap.read()
    if success:
        cv2.imwrite(thumbnail_path, image)
    cap.release()

# Decorator to mark a function as internal
def internal(func):
    func.__internal__ = True
    return func