from _utils import Singleton, internal
import _utils
from pymongo import MongoClient, DESCENDING
from constant import DetectStatusCode as DSC, CameraStatusCode as CSC
import time

class Database(Singleton):
    
    host = 'mongodb://localhost:27017/'
    auth_user = 'admin'
    auth_pswd = '12345678'
    auth_source = 'admin'
    db_name = 'test'
    
    def __init__(self):
        pass
    
    @internal
    def _cursor2array(self, cursor) -> list:
        return [doc for doc in cursor]
    _c2a = _cursor2array
    
    @internal
    def _connect(self):
        return MongoClient(self.host,
                           username=self.auth_user,
                           password=self.auth_pswd,
                           authSource=self.auth_source)
        
    # AUTH DB OPERATIONS
    def createUser(self, username: str, password: str, loginToken: str = "", tokenExpire: int = -1, sensitivity: int = 0) -> None:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.insert_one({
                'username': username,
                'password': password,
                'loginToken': loginToken,
                'tokenExpire': tokenExpire,
                'sensitivity': sensitivity,
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
    
    def getUser(self, username: str) -> None|dict:
        user = self._getUser(username)
        if len(user) == 0:
            return None
        return user[0]
    
    def getUserByToken(self, loginToken: str) -> None|dict:
        user = self._getByToken(loginToken)
        if len(user) == 0:
            return None
        return user[0]
        
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
            
    def getUserSensitivity(self, username: str) -> int:
        user = self._getUser(username)
        if len(user) == 0:
            return -1
        return user[0]['sensitivity']
    
    # CAMERA OPERATIONS
    def createCamera(self, cameraId: str, cameraName: str, username: str = "", linkCode: str = "", status: int = CSC.UNKNOWN):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            collection.insert_one({
                'cameraId': cameraId,
                'cameraName': cameraName,
                'username': username,
                'linkCode': "",
                'status': 0
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
        
    def getCamera(self, cameraId: str) -> None|dict:
        camera = self._getCamera(cameraId)
        if len(camera) == 0:
            return None
        return camera[0]
            
    def getUserCameras(self, username: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            cursor = collection.find({'username': username})
            return self._c2a(cursor)
        
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
            if len(self._c2a(cursor)) == 0:
                return False
            cameraId = self._c2a(cursor)[0]['cameraId']
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
    
    # Detect Data things
    def insertDetectData(self, uuid: str, cameraId: str, beginTimeStamp: int, endTimeStamp: int, statusCode: int = DSC.UNKNOWN):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.insert_one({
                'uuid': uuid,
                'cameraId': cameraId,
                'beginTimeStamp': beginTimeStamp,
                'endTimeStamp': endTimeStamp,
                'statusCode': statusCode
            })
    
    @internal
    def _getDetectData(self, uuid: str):
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'uuid': uuid})
            return self._c2a(cursor)
        
    def getDetectData(self, uuid: str) -> None|dict:
        result = self._getDetectData(uuid)
        if len(result) == 0:
            return None
        return result[0]
    
    def getDetectDataByCameraId(self, cameraId: str) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'cameraId': cameraId}).sort('beginTime', DESCENDING)
            return self._c2a(cursor)
        
    def getDetectDataByUser(self, username: str) -> list:
        cameras = self.getUserCameras(username)
        if len(cameras) == 0:
            return []
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find(
                {'cameraId': {'$in': [camera['cameraId'] for camera in cameras]}}
            ).sort('beginTime', DESCENDING)
            return self._c2a(cursor)
        
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
            
    def getDetectDataByTimeRange(self, beginTimeStamp: int, endTimeStamp: int) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({
                'beginTimeStamp': {'$gte': beginTimeStamp}, 
                'endTimeStamp': {'$lte': endTimeStamp}
            }).sort('beginTime', DESCENDING)
            return self._c2a(cursor)
        
    def getDetectDataByStatusCode(self, statusCode: int) -> list:
        with self._connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'statusCode': statusCode}).sort('beginTime', DESCENDING)
            return self._c2a(cursor)
    