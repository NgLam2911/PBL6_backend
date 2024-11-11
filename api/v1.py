from flask import Blueprint
from flask_restx import Api, Resource, fields
from dbs import Database
import api.parsers as parsers
import _utils
from constant import CameraStatusCode as CSC, DetectStatusCode as DSC
from http import HTTPStatus
import werkzeug

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
        if result is None:
            return {'error': 'Invalid username or password'}, HTTPStatus.BAD_REQUEST
        return {'token': result}, HTTPStatus.OK
    
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
        if check is not None:
            return {'error': 'User already exists'}, HTTPStatus.BAD_REQUEST
        db.registerUser(username, password)
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
        if user is None:
            return {'error': 'Invalid username or password'}, HTTPStatus.BAD_REQUEST
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
        if camera is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        db.insertDetectData(actionId, cameraId, beginTime, endTime)
        return {'actionId': actionId}, HTTPStatus.OK

@detect_api.route('/video')
@detect_api.doc(description='Upload a video of a detected action')
class UploadVideo(Resource):
    @detect_api.expect(parsers.upload_parser)
    @detect_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @detect_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @detect_api.marshal_with(models.success_model, code=HTTPStatus.OK)
    def post(self):
        args = parsers.upload_parser.parse_args()
        actionId = args['actionId']
        file = args['file']
        file_ext = file.filename.split('.')[-1]
        action = db.getDetectData(actionId)
        if action is None:
            return {'error': 'Invalid actionId'}, HTTPStatus.BAD_REQUEST
        if not isinstance(file, werkzeug.datastructures.FileStorage):
            return {'error': 'Invalid file'}, HTTPStatus.BAD_REQUEST
        file.save(f'./videos/{actionId}.{file_ext}')
        db.updateDetectData(actionId, DSC.RECEIVED)
        return {'message': 'Video uploaded'}, HTTPStatus.OK

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
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        cameraId = args['cameraId']
        camera = None
        if cameraId is not None:
            camera = db.getCamera(cameraId)
            if camera is None:
                return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
            userCam = camera['username']
            if userCam != user['username']:
                return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        if camera is None:
            data = db.getDetectDataByUser(user['username'])
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
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        actionId = args['actionId']
        data = db.getDetectData(actionId)
        camera = db.getCamera(data['cameraId'])
        user = db.getUserByToken(token)
        if user['username'] != camera['username']:
            return {'error': 'You do not have access to this data'}, HTTPStatus.UNAUTHORIZED
        if data is None:
            return {'error': 'Invalid actionId'}, HTTPStatus.BAD_REQUEST
        return data, HTTPStatus.OK
    
# TODO: All of this API method need database structure update to be able to implement  
    
@camera_api.route('/register')
@camera_api.doc(description='Use to assign a new camera hardware with new ID and Linking Code')
class RegisterCamera(Resource):
    @camera_api.marshal_with(models.register_camera_model, code=HTTPStatus.OK)
    def get(self):
        cameraId = _utils.generateCameraId()
        linkingCode = _utils.generateLinkingCode()
        db.registerCamera(cameraId=cameraId, linkingCode=linkingCode, status=CSC.NOT_LINKED)
        return {'cameraId': cameraId, 'linkingCode': linkingCode}, HTTPStatus.OK
        
@camera_api.route('/get')
@camera_api.doc(description='Get camera information')
class GetCamera(Resource):
    @camera_api.expect(parsers.camera_parser)
    @camera_api.marshal_with(models.camera_model, code=HTTPStatus.OK)
    @camera_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @camera_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    def get(self):
        args = parsers.get_camera_parser.parse_args()
        token = args['token']
        cameraId = args['cameraId']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        camera = db.getCamera(cameraId)
        if camera is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        user = db.getUserByToken(token)
        if camera['username'] != user['username']:
            return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
        return camera, HTTPStatus.OK
    
@camera_api.route('/getall')
@camera_api.doc(description='Get all cameras that a user has access to')
class GetAllCamera(Resource):
    @camera_api.expect(parsers.get_all_camera_parser)
    @camera_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @camera_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @camera_api.marshal_with([models.camera_model], code=HTTPStatus.OK)
    def get(self):
        args = parsers.get_all_camera_parser.parse_args()
        token = args['token']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        cameras = db.getUserCameras(user['username'])
        return cameras, HTTPStatus.OK
    
@camera_api.route('/rename')
@camera_api.doc(description='Rename a camera')
class RenameCamera(Resource):
    @camera_api.expect(parsers.rename_camera_parser)
    @camera_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @camera_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @camera_api.marshal_with(models.success_model, code=HTTPStatus.OK)
    def post(self):
        args = parsers.rename_camera_parser.parse_args()
        token = args['token']
        cameraId = args['cameraId']
        name = args['name']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        camera = db.getCamera(cameraId)
        if camera is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        user = db.getUserByToken(token)
        if user['username'] != camera['username']:
            return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
        db.renameCamera(cameraId, name)

@camera_api.route('/delete')
@camera_api.doc(description='Delete a camera')
class DeleteCamera(Resource):
    @camera_api.expect(parsers.camera_parser)
    @camera_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @camera_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @camera_api.marshal_with(models.success_model, code=HTTPStatus.OK)
    def delete(self):
        args = parsers.camera_parser.parse_args()
        token = args['token']
        cameraId = args['cameraId']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        camera = db.getCamera(cameraId)
        if camera is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        user = db.getUserByToken(token)
        if user['username'] != camera['username']:
            return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
        db.deleteCamera(cameraId)
        return {'message': 'Camera deleted'}, HTTPStatus.OK
        
    
@camera_api.route('/link')
@camera_api.doc(description='Link a camera hardware with a camera ID to a user with a linking code')
class LinkCamera(Resource):
    @camera_api.expect(parsers.link_camera_parser)
    @camera_api.marshal_with(models.error_model, code=HTTPStatus.BAD_REQUEST)
    @camera_api.marshal_with(models.authenticate_fail_model, code=HTTPStatus.UNAUTHORIZED)
    @camera_api.marshal_with(models.success_model, code=HTTPStatus.OK)
    def post(self):
        args = parsers.link_camera_parser.parse_args()
        token = args['token']
        linkingCode = args['linkingCode']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        result = db.linkCamera(user['username'], linkingCode)
        if result:
            return {'message': 'Camera linked'}, HTTPStatus.OK
        return {'error': 'Invalid linking code'}, HTTPStatus.BAD_REQUEST
    
    

        



