from .class_pattern import Singleton

import uuid as uuid_generator
import base64
import time

def generateToken():
    return base64.b64encode(generateUUID().encode()).decode()

def generateUUID():
    return str(uuid_generator.uuid4())

def hms2unix(hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    return hours * 3600 + minutes * 60 + seconds

def unixNow() -> int:
    return int(time.time())