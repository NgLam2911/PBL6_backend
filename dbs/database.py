from _utils import Singleton
from pymongo import MongoClient
from constant import DetectStatusCode as DSC, SortOrder
import time

class Database(Singleton):
    
    host = 'mongodb://localhost:27017/'
    auth_user = 'admin'
    auth_pswd = '12345678'
    auth_source = 'admin'
    db_name = 'test'
    
    def __init__(self):
        pass
    
    def cursor2array(self, cursor):
        return [doc for doc in cursor]
    
    def connect(self):
        return MongoClient(self.host,
                           username=self.auth_user,
                           password=self.auth_pswd,
                           authSource=self.auth_source)
    
    def insertDetectData(self, uuid: str, cameraId: str, beginTimeStamp: int, endTimeStamp: int, statusCode: int = DSC.UNKNOWN):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.insert_one({
                'uuid': uuid,
                'cameraId': cameraId,
                'beginTimeStamp': beginTimeStamp,
                'endTimeStamp': endTimeStamp,
                'statusCode': statusCode
            })
    
    def getDetectData(self, uuid: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'uuid': uuid})
            return self.cursor2array(cursor)
    
    def getDetectDataByCameraId(self, cameraId: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'cameraId': cameraId}).sort('beginTime', SortOrder.DESCENDING)
            return self.cursor2array(cursor)
        
    def getDetectDataByUser(self, username: str):
        cameras = self.getUserCameras(username)
        if len(cameras) == 0:
            return []
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find(
                {'cameraId': {'$in': [camera['cameraId'] for camera in cameras]}}
            ).sort('beginTime', SortOrder.DESCENDING)
            return self.cursor2array(cursor)
        
    def updateDetectData(self, uuid: str, statusCode: int):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.update_one({'uuid': uuid}, {'$set': {'statusCode': statusCode}})
            
    def deleteDetectData(self, uuid: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.delete_one({'uuid': uuid})
            
    def getDetectDataByTimeRange(self, beginTimeStamp: int, endTimeStamp: int):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({
                'beginTimeStamp': {'$gte': beginTimeStamp}, 
                'endTimeStamp': {'$lte': endTimeStamp}
            }).sort('beginTime', SortOrder.DESCENDING)
            return self.cursor2array(cursor)
        
    def getDetectDataByStatusCode(self, statusCode: int):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'statusCode': statusCode}).sort('beginTime', SortOrder.DESCENDING)
            return self.cursor2array(cursor)
        
    # Auth
    
    def createUser(self, username: str, password: str, loginToken: str = "", tokenExpire: int = -1):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.insert_one({
                'username': username,
                'password': password,
                'loginToken': loginToken,
                'tokenExpire': tokenExpire,
            })
            
    def addCamera(self, username: str, cameraId: str, cameraName: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one(
                {'username': username},
                {'$push': {'cameras': {
                    'cameraId': cameraId, 
                    'cameraName': cameraName
                }}}
            )
            
    def removeCamera(self, username: str, cameraId: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one(
                {'username': username},
                {'$pull': {'cameras': {'cameraId': cameraId}}}
            )
            
    def getUserCameras(self, username: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'username': username})
            array = self.cursor2array(cursor)
            if len(array) == 0:
                return []
            cameras = array[0]['cameras']
            return cameras
        
    def getCamera(self, cameraId: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['cameras']
            cursor = collection.find({'cameraId': cameraId})
            return self.cursor2array(cursor)
        
    def loginUser(self, username: str, password: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'username': username, 'password': password})
            return self.cursor2array(cursor)
        
    def updateUserToken(self, username: str, loginToken: str, tokenExpire: int):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.update_one(
                {'username': username}, 
                {'$set': {'loginToken': loginToken, 'tokenExpire': tokenExpire}}
            )
        
    def loginByToken(self, loginToken: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'loginToken': loginToken, 'tokenExpire': {'$gt': int(time.time())}})
            return self.cursor2array(cursor)
        
    def deleteUser(self, username: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            collection.delete_one({'username': username})
            
    def getUser(self, username: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['users']
            cursor = collection.find({'username': username})
            return self.cursor2array(cursor)
        
    # Linking cameras to users things
    
    def newLink(self, cameraId: str, linkCode: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['link']
            collection.insert_one({
                'cameraId': cameraId,
                'linkCode': linkCode
            })
    
    def getLink(self, linkCode: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['link']
            cursor = collection.find({'linkCode': linkCode})
            return self.cursor2array(cursor)
        
    def deleteLink(self, linkCode: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['link']
            collection.delete_one({'linkCode': linkCode})
            
    def getCameraByLink(self, linkCode: str):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['link']
            cursor = collection.find({'linkCode': linkCode})
            array = self.cursor2array(cursor)
            if len(array) == 0:
                return []
            return self.getCamera(array[0]['cameraId'])
    