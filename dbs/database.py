from _utils import Singleton, internal
import _utils
from pymongo import MongoClient, DESCENDING
from constant import DetectStatusCode as DSC, CameraStatusCode as CSC
import time
import os
from dotenv import load_dotenv
from .entities import *

class Database(Singleton):
    
    def __init__(self):
        load_dotenv() # FUCK LINUX
        self.host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        if self.host is None:
            raise Exception("DB_HOST not found in environment variables")
        if self.db_name is None:
            raise Exception("DB_NAME not found in environment variables")
        pass
    
    @internal
    def _cursor2array(self, cursor) -> list:
        return [doc for doc in cursor]
    _c2a = _cursor2array
    
    @internal
    def _connect(self):
        return MongoClient(self.host)
        
    # AUTH DB OPERATIONS
    def createUser(self, username: str, 
                   password: str, 
                   loginToken: str = "", 
                   tokenExpire: int = -1, 
                   sensitivity: int = 0,
                   notification: bool = True,
                   monitoring: bool = True,
                   fcm_token: str = "") -> None:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.insert_one({
                'username': username,
                'password': password,
                'loginToken': loginToken,
                'tokenExpire': tokenExpire,
                'sensitivity': sensitivity,
                'notification': notification,
                'monitoring': monitoring,
                'fcm_token': fcm_token
            })
    registerUser = createUser
    
    @internal
    def _loginUser(self, username: str, password: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'username': username, 'password': password})
            return self._c2a(cursor)
        
    def loginUser(self, username: str, password: str) -> None|str:
        result = self._loginUser(username, password)
        if len(result) == 0:
            return None
        token = _utils.generateToken()
        expire = _utils.unixNow() + _utils.hms2unix(hours=10)
        self._updateUserToken(username, token, expire)  
        return token
    
    @internal    
    def _updateUserToken(self, username: str, loginToken: str, tokenExpire: int) -> None:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one(
                {'username': username}, 
                {'$set': {'loginToken': loginToken, 'tokenExpire': tokenExpire}}
            )
    
    @internal    
    def _getByToken(self, loginToken: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'loginToken': loginToken, 'tokenExpire': {'$gt': int(time.time())}})
            return self._c2a(cursor)
        
    def loginByToken(self, loginToken: str) -> bool:
        return len(self._getByToken(loginToken)) > 0
    authenticate = loginByToken
        
    def deleteUser(self, username: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.delete_one({'username': username})
    
    @internal        
    def _getUser(self, username: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'username': username})
            return self._c2a(cursor)
    
    def getUser(self, username: str) -> None|User:
        user = self._getUser(username)
        if len(user) == 0:
            return None
        return User.fromDict(user[0])
    
    def getUserByToken(self, loginToken: str) -> None|User:
        user = self._getByToken(loginToken)
        if len(user) == 0:
            return None
        return User.fromDict(user[0])
        
    def changePassword(self, username: str, password: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one({'username': username}, {'$set': {'password': password}})
    updatePassword = changePassword
    
    def updateUserSensitivity(self, username: str, sensitivity: int):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one({'username': username}, {'$set': {'sensitivity': sensitivity}})
    
    def updateUserNotification(self, username: str, notification: bool):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one({'username': username}, {'$set': {'notification': notification}})
            
    def updateUserMonitoring(self, username: str, monitoring: bool):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one({'username': username}, {'$set': {'monitoring': monitoring}})
            
    def updateUserFCMToken(self, username: str, fcm_token: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one({'username': username}, {'$set': {'fcm_token': fcm_token}})
            
    def updateUser(self, user: User):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one({'username': user.username}, {'$set': user.toDict()})
    
    # CAMERA OPERATIONS
    def createCamera(self, cameraId: str, cameraName: str, username: str = "", linkCode: str = "", status: int = CSC.UNKNOWN):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.insert_one({
                'cameraId': cameraId,
                'cameraName': cameraName,
                'username': username,
                'linkCode': linkCode,
                'status': status
            })
    registerCamera = createCamera
            
    def removeCamera(self, cameraId: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.delete_one({'cameraId': cameraId})
    
    @internal     
    def _getCamera(self, cameraId: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            cursor = collection.find({'cameraId': cameraId})
            return self._c2a(cursor)
        
    def getCamera(self, cameraId: str) -> None|Camera:
        camera = self._getCamera(cameraId)
        if len(camera) == 0:
            return None
        return Camera.fromDict(camera[0])
    
    @internal        
    def _getUserCameras(self, username: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            cursor = collection.find({'username': username})
            return self._c2a(cursor)
        
    def getUserCameras(self, username: str) -> list:
        return [Camera.fromDict(camera) for camera in self._getUserCameras(username)]
        
    def updateCameraStatus(self, cameraId: str, status: int):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.update_one({'cameraId': cameraId}, {'$set': {'status': status}})
            
    def updateCameraLinkCode(self, cameraId: str, linkCode: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.update_one({'cameraId': cameraId}, {'$set': {'linkCode': linkCode}})
  
    def linkCamera(self, username: str, linkCode: str) -> bool:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            cursor = collection.find({'linkCode': linkCode, 'status': CSC.NOT_LINKED})
            data = self._c2a(cursor)
            if len(data) == 0:
                return False
            cameraId = data[0]['cameraId']
            collection.update_one({'cameraId': cameraId}, {'$set': {'username': username, 'status': CSC.LINKED, 'linkCode': ""}})
            return True
        
    def updateCameraName(self, cameraId: str, cameraName: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.update_one({'cameraId': cameraId}, {'$set': {'cameraName': cameraName}})
    changeCameraName = renameCamera = updateCameraName
    
    def deleteCamera(self, cameraId: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.delete_one({'cameraId': cameraId})
            
    def updateCamera(self, camera: Camera):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.update_one({'cameraId': camera.camera_id}, {'$set': camera.toDict()})
    
    # Detect Data things
    def insertDetectData(self, uuid: str, cameraId: str, beginTimeStamp: int, endTimeStamp: int, statusCode: int = DSC.UNKNOWN, accuracy: float = -1.0):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.insert_one({
                'uuid': uuid,
                'cameraId': cameraId,
                'beginTimeStamp': beginTimeStamp,
                'endTimeStamp': endTimeStamp,
                'statusCode': statusCode,
                'accuracy': accuracy
            })
    
    @internal
    def _getDetectData(self, uuid: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'uuid': uuid})
            return self._c2a(cursor)
        
    def getDetectData(self, uuid: str) -> None|Action:
        result = self._getDetectData(uuid)
        if len(result) == 0:
            return None
        return Action.fromDict(result[0])
    
    @internal
    def _getDetectDataByCameraId(self, cameraId: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'cameraId': cameraId}).sort('beginTimeStamp', DESCENDING)
            return self._c2a(cursor)
        
    def getDetectDataByCameraId(self, cameraId: str) -> list:
        return [Action.fromDict(action) for action in self._getDetectDataByCameraId(cameraId)]
    
    @internal    
    def _getDetectDataByUser(self, username: str) -> list:
        cameras = self.getUserCameras(username)
        if len(cameras) == 0:
            return []
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find(
                {'cameraId': {'$in': [camera.cameraId for camera in cameras]}}
            ).sort('beginTimeStamp', DESCENDING)
            return self._c2a(cursor)
        
    def getDetectDataByUser(self, username: str) -> list:
        return [Action.fromDict(action) for action in self._getDetectDataByUser(username)]
        
    def updateDetectData(self, uuid: str, statusCode: int):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.update_one({'uuid': uuid}, {'$set': {'statusCode': statusCode}})
            
    def deleteDetectData(self, uuid: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.delete_one({'uuid': uuid})
    
    @internal        
    def _getDetectDataByTimeRange(self, beginTimeStamp: int, endTimeStamp: int) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({
                'beginTimeStamp': {'$gte': beginTimeStamp}, 
                'endTimeStamp': {'$lte': endTimeStamp}
            }).sort('beginTimeStamp', DESCENDING)
            return self._c2a(cursor)
        
    def getDetectDataByTimeRange(self, beginTimeStamp: int, endTimeStamp: int) -> list:
        return [Action.fromDict(action) for action in self._getDetectDataByTimeRange(beginTimeStamp, endTimeStamp)]
        
    @internal
    def _getUserDetectDataByTimeRange(self, username: str, beginTimeStamp: int, endTimeStamp: int) -> list:
        cameras = self.getUserCameras(username)
        if len(cameras) == 0:
            return []
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({
                'cameraId': {'$in': [camera.cameraId for camera in cameras]},
                'beginTimeStamp': {'$gte': beginTimeStamp}, 
                'endTimeStamp': {'$lte': endTimeStamp}
            }).sort('beginTimeStamp', DESCENDING)
            return self._c2a(cursor)
    
    def getUserDetectDataByTimeRange(self, username: str, beginTimeStamp: int, endTimeStamp: int) -> list:
        return [Action.fromDict(action) for action in self._getUserDetectDataByTimeRange(username, beginTimeStamp, endTimeStamp)]
    
    @internal    
    def _getCameraDetectDataByTimeRange(self, cameraId: str, beginTimeStamp: int, endTimeStamp: int) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({
                'cameraId': cameraId,
                'beginTimeStamp': {'$gte': beginTimeStamp}, 
                'endTimeStamp': {'$lte': endTimeStamp}
            }).sort('beginTimeStamp', DESCENDING)
            return self._c2a(cursor)
        
    def getCameraDetectDataByTimeRange(self, cameraId: str, beginTimeStamp: int, endTimeStamp: int) -> list:
        return [Action.fromDict(action) for action in self._getCameraDetectDataByTimeRange(cameraId, beginTimeStamp, endTimeStamp)]
    
    @internal    
    def _getDetectDataByStatusCode(self, statusCode: int) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'statusCode': statusCode}).sort('beginTimeStamp', DESCENDING)
            return self._c2a(cursor)
       
    def getDetectDataByStatusCode(self, statusCode: int) -> list:
        return [Action.fromDict(action) for action in self._getDetectDataByStatusCode(statusCode)]
    
    def updateAction(self, action: Action):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.update_one({'uuid': action.uuid}, {'$set': action.toDict()})
            
    