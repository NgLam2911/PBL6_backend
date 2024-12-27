from constant import CameraStatusCode as CSC, DetectStatusCode as DSC

class User:
    def __init__(self, 
                username: str,
                password: str,
                loginToken: str = "",
                tokenExpire: int = 0,
                sensitivity: int = 0,
                notification: bool = True,
                monitoring: bool = True,
                fcm_token: str = ""):
        self.username = username
        self.password = password
        self.loginToken = loginToken
        self.tokenExpire = tokenExpire
        self.sensitivity = sensitivity
        self.notification = notification
        self.monitoring = monitoring
        self.fcm_token = fcm_token
        
    @staticmethod
    def fromDict(d: dict):
        fields = ["username", "password", "loginToken", "tokenExpire", "sensitivity", "notification", "monitoring", "fcm_token"]
        values = {
            "username": "",
            "password": "",
            "loginToken": "",
            "tokenExpire": 0,
            "sensitivity": 0,
            "notification": True,
            "monitoring": True,
            "fcm_token": ""
        }
        for field in fields:
            if field in d:
                values[field] = d[field]
        return User(**values)
    
    def toDict(self):
        return {
            "username": self.username,
            "password": self.password,
            "loginToken": self.loginToken,
            "tokenExpire": self.tokenExpire,
            "sensitivity": self.sensitivity,
            "notification": self.notification,
            "monitoring": self.monitoring,
            "fcm_token": self.fcm_token
        }
        
    def __str__(self):
        return f"user: {self.username}"
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.username == other.username
    
    def __hash__(self):
        return hash(self.username)
    
class Camera:
    def __init__(self, 
                cameraId: str,
                cameraName: str = "",
                username: str = "",
                linkCode: str = "",
                status: int = CSC.UNKNOWN):
        self.cameraId = cameraId
        self.cameraName = cameraName
        self.username = username
        self.linkCode = linkCode
        self.status = status
    
    @staticmethod
    def fromDict(d: dict):
        fields = ["cameraId", "cameraName", "username", "linkCode", "status"]
        values = {
            "cameraId": "",
            "cameraName": "",
            "username": "",
            "linkCode": "",
            "status": CSC.UNKNOWN
        }
        for field in fields:
            if field in d:
                values[field] = d[field]
        return Camera(**values)
    
    def toDict(self):
        return {
            "cameraId": self.cameraId,
            "cameraName": self.cameraName,
            "username": self.username,
            "linkCode": self.linkCode,
            "status": self.status
        }
        
    def __str__(self):
        return f"camera: {self.cameraId}"
    
    def __eq__(self, other):
        if not isinstance(other, Camera):
            return False
        return self.cameraId == other.cameraId
    
    def __hash__(self):
        return hash(self.cameraId)
    
    def user(self) -> None|User:
        from dbs import Database
        db = Database()
        return db.getUser(self.username)
    
class Action:
    def __init__(self,
                uuid: str,
                cameraId: str,
                beginTimeStamp: int,
                endTimeStamp: int,
                status: int = DSC.UNKNOWN,
                accuracy: float = -1.0):
        self.uuid = uuid
        self.cameraId = cameraId
        self.beginTimeStamp = beginTimeStamp
        self.endTimeStamp = endTimeStamp
        self.status = status
        self.accuracy = accuracy
        
    @staticmethod
    def fromDict(d: dict):
        fields = ["uuid", "cameraId", "beginTimeStamp", "endTimeStamp", "status", "accuracy"]
        values = {
            "uuid": "",
            "cameraId": "",
            "beginTimeStamp": 0,
            "endTimeStamp": 0,
            "status": DSC.UNKNOWN,
            "accuracy": -1.0
        }
        for field in fields:
            if field in d:
                values[field] = d[field]
        return Action(**values)
    
    def toDict(self):
        return {
            "uuid": self.uuid,
            "cameraId": self.cameraId,
            "beginTimeStamp": self.beginTimeStamp,
            "endTimeStamp": self.endTimeStamp,
            "status": self.status,
            "accuracy": self.accuracy
        }
        
    def __str__(self):
        return f"action: {self.uuid}"
    
    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return self.uuid == other.uuid
    
    def __hash__(self):
        return hash(self.uuid)
    
    def camera(self) -> None|Camera:
        from dbs import Database
        db = Database()
        return db.getCamera(self.cameraId)
    
