from flask import Blueprint
from flask_restx import Api, Resource, fields
from dbs import Database
import api.parsers as parsers
import _utils
from http import HTTPStatus

v1service = Blueprint('api/v1', __name__, url_prefix='/api/v1')
api = Api(v1service, version='0.0.1', title='V1 API', description='Indev API')
import api.models as models
db = Database()

auth_api = api.namespace('auth', description='Auth operations')
detect_api = api.namespace('detect', description='Detect operations')
camera_api = api.namespace('camera', description='Camera operations')

@auth_api.route('/login')
@auth_api.doc(description='Login to the system, return a token')
class Login(Resource):
    @auth_api.expect(parsers.user_parser)
    @auth_api.marshal_with(models.login_success_model, code=HTTPStatus.OK)
    @auth_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    def post(self):
        args = parsers.user_parser.parse_args()
        username = args['username']
        password = args['password']
        result = db.loginUser(username, password)
        if len(result) > 0:
            token = result[0]['loginToken']
            if (token == "") or (result[0]['tokenExpire'] < _utils.unixNow()):
                token = _utils.generateToken()
                expireTime = _utils.unixNow() + _utils.hms2unix(hours=10)
                db.updateUserToken(username, token, expireTime)
            return {'token': token}, HTTPStatus.OK
        return {'error': 'Invalid username or password'}, HTTPStatus.BAD_REQUEST
    
@auth_api.route('/register')
@auth_api.doc(description='Register a new user')
class Register(Resource):
    @auth_api.expect(parsers.user_parser)
    @auth_api.marshal_with(models.register_success_model, code=HTTPStatus.OK)
    @auth_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    def post(self):
        args = parsers.user_parser.parse_args()
        username = args['username']
        password = args['password']
        check = db.getUser(username)
        if len(check) > 0:
            return {'error': 'Username already exists'}, HTTPStatus.BAD_REQUEST
        db.createUser(username, password)
        return {'message': 'User registered'}, HTTPStatus.OK
    
@auth_api.route('changePassword')
@auth_api.doc(description='Change password of a user')
class ChangePassword(Resource):
    @auth_api.expect(parsers.changepwd_parser)
    @auth_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @auth_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @auth_api.marshal_with(models.success_model, code=HTTPStatus.OK)
    def post(self):
        args = parsers.changepwd_parser.parse_args()
        username = args['username']
        oldPassword = args['oldPassword']
        newPassword = args['newPassword']
        user = db.loginUser(username, oldPassword)
        if len(user) == 0:
            return {'error': 'Invalid username or password'}, HTTPStatus.UNAUTHORIZED
        db.changePassword(username, newPassword)
        return {'message': 'Password changed'}, HTTPStatus.OK
    
@detect_api.route('/report')
@detect_api.doc(description='Report a detected action')
class Report(Resource):
    @detect_api.expect(parsers.report_parser)
    @detect_api.marshal_with(models.report_model, code=HTTPStatus.OK)
    @detect_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    def post(self):
        args = parsers.report_parser.parse_args()
        cameraId = args['cameraId']
        beginTime = args['beginTime']
        endTime = args['endTime']
        actionId = _utils.generateUUID()
        # Check if cameraId exists
        camera = db.getCamera(cameraId)
        if len(camera) == 0:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        db.insertDetectData(actionId, cameraId, beginTime, endTime)
        return {'actionId': actionId}, HTTPStatus.OK
    
@detect_api.route('/getall')
@detect_api.doc(description='Get all detect data')
class GetAllDetect(Resource):
    @detect_api.expect(parsers.detect_getAll_parser)
    @detect_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @detect_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @detect_api.marshal_with([models.detectData_model], code=HTTPStatus.OK)
    def get(self):
        args = parsers.detect_getAll_parser.parse_args()
        token = args['token']
        user = db.loginByToken(token)
        if len(user) == 0:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        pass
        cameraId = args['cameraId']
        camera = None
        if cameraId is not None:
            camera = db.getCamera(cameraId)
            if len(camera) == 0:
                return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
            userCam = db.getUserCameras(user[0]['username'])
            if camera[0]['cameraId'] not in [c['cameraId'] for c in userCam]:
                return {'error': "This user doesn't have permission to access this camera"}, HTTPStatus.UNAUTHORIZED
        if camera is None:
            data = db.getDetectDataByUser(user[0]['username'])
        else:
            data = db.getDetectDataByCameraId(cameraId)
        return data, HTTPStatus.OK
    
@detect_api.route('/get')
@detect_api.doc(description='Get a specific detect data')
class GetDetect(Resource):
    @detect_api.expect(parsers.detect_get_parser)
    @detect_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @detect_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @detect_api.marshal_with(models.detectData_model, code=HTTPStatus.OK)
    def get(self):
        args = parsers.detect_get_parser.parse_args()
        token = args['token']
        user = db.loginByToken(token)
        if len(user) == 0:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        actionId = args['actionId']
        data = db.getDetectData(actionId)
        if len(data) == 0:
            return {'error': 'Action not found'}, HTTPStatus.NOT_FOUND
        return data[0], HTTPStatus.OK
    
# TODO: All of this API method need database structure update to be able to implement  
    
@camera_api.route('/register')
@camera_api.doc(description='Use to assign a new camera hardware with new ID and Linking Code')
class RegisterCamera(Resource):
    def get(self):
        pass
    
@camera_api.route('/get')
@camera_api.doc(description='Get camera information')
class GetCamera(Resource):
    def get(self):
        pass
    
@camera_api.route('/getall')
@camera_api.doc(description='Get all cameras that a user has access to')
class GetAllCamera(Resource):
    def get(self):
        pass
    
@camera_api.route('/rename')
@camera_api.doc(description='Rename a camera')
class RenameCamera(Resource):
    def post(self):
        pass

@camera_api.route('/delete')
@camera_api.doc(description='Delete a camera')
class DeleteCamera(Resource):
    def delete(self):
        pass
    
@camera_api.route('/link')
@camera_api.doc(description='Link a camera hardware with a camera ID to a user with a linking code')
class LinkCamera(Resource):
    def post(self):
        pass
    
    

        



