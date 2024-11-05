from _utils import Singleton
from pymongo import MongoClient
from constant import DetectStatusCode as DSC
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
    
    def insertDetectData(self, uuid: str, beginTimeStamp: int, endTimeStamp: int, statusCode: int = DSC.UNKNOWN):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            collection.insert_one({
                'uuid': uuid,
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
            cursor = collection.find({'beginTimeStamp': {'$gte': beginTimeStamp}, 'endTimeStamp': {'$lte': endTimeStamp}})
            return self.cursor2array(cursor)
        
    def getDetectDataByStatusCode(self, statusCode: int):
        with self.connect() as client:
            db = client[self.db_name]
            collection = db['detect_data']
            cursor = collection.find({'statusCode': statusCode})
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
                'tokenExpire': tokenExpire
            })
        
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
    