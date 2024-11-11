from enum import IntEnum

class DetectStatusCode(IntEnum):
    UNKNOWN = 0
    PENDING = 1
    PROCESSING = 2
    RECEIVED = 3
    TIMED_OUT = 4
    ERROR = 5
    
class CameraStatusCode(IntEnum):
    UNKNOWN = 0
    NOT_LINKED = 1
    LINKED = 2