from enum import IntEnum

class DetectStatusCode(IntEnum):
    UNKNOWN = 0
    PENDING = 1
    PROCESSING = 2
    RECEIVED = 3
    TIMED_OUT = 4
    ERROR = 5
    
class ApiRequestStatusCode(IntEnum):
    SUCCESS = 200
    NOT_FOUND = 404
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500
    UNAUTHORIZED = 401
    