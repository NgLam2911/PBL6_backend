from flask import Blueprint
from flask_restx import Api, Resource, fields
from dbs import Database
import api.parsers as parsers
import _utils
from constant import CameraStatusCode as CSC, DetectStatusCode as DSC
from http import HTTPStatus
import werkzeug
import os
from dotenv import load_dotenv


v1service = Blueprint('api/v1', __name__, url_prefix='/api/v1')
api = Api(v1service, version='0.1.0', title='V1 API', description='Indev API')
import api.models as models
db = Database()
notif = _utils.Notificator()

auth_api = api.namespace('auth', description='Auth operations')
detect_api = api.namespace('detect', description='Detect operations')
camera_api = api.namespace('camera', description='Camera operations')

@auth_api.route('/login')
@auth_api.doc(description='Login to the system, return a token')
class Login(Resource):
    @auth_api.expect(parsers.user_parser)
    @auth_api.response(HTTPStatus.OK, 'Login successful', models.login_success_model)
    @auth_api.response(HTTPStatus.BAD_REQUEST, 'Invalid username or password', models.error_model)
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
    @auth_api.response(HTTPStatus.OK, 'User registered', models.register_success_model)
    @auth_api.response(HTTPStatus.BAD_REQUEST, 'User already exists', models.error_model)
    def post(self):
        args = parsers.user_parser.parse_args()
        username = args['username']
        password = args['password']
        check = db.getUser(username)
        if check is not None:
            return {'error': 'User already exists'}, HTTPStatus.BAD_REQUEST
        db.registerUser(username, password)
        return {'message': 'User registered'}, HTTPStatus.OK
    
@auth_api.route('/changePassword')
@auth_api.doc(description='Change password of a user')
class ChangePassword(Resource):
    @auth_api.expect(parsers.changepwd_parser)
    @auth_api.response(HTTPStatus.BAD_REQUEST, 'Invalid username or password', models.error_model)
    @auth_api.response(HTTPStatus.OK, 'Password changed', models.success_model)
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
    
@auth_api.route('/getsettings')
@auth_api.doc(description='Get user settings information')
class GetUserSettings(Resource):
    @auth_api.expect(parsers.token_parser)
    @auth_api.response(HTTPStatus.OK, 'User settings', models.userSettings_model)
    @auth_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    def get(self):
        args = parsers.token_parser.parse_args()
        token = args['token']
        if (not db.authenticate(token)):
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        return {
            'username': user.username,
            'notification': user.notification,
            'monitoring': user.monitoring,
            'fcm_token': user.fcm_token,
            'sensitivity': user.sensitivity
        }, HTTPStatus.OK
        
@auth_api.route('/sensitivity')
@auth_api.doc(description='Change sensitivity of a user')
class UserSensitivity(Resource):
    @auth_api.expect(parsers.sensitivity_parser)
    @auth_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @auth_api.response(HTTPStatus.OK, 'Sensitivity changed', models.success_model)
    def post(self):
        args = parsers.sensitivity_parser.parse_args()
        token = args['token']
        sensitivity = args['sensitivity']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        db.updateUserSensitivity(user.username, sensitivity)
        return {'message': 'sensitivity changed'}, HTTPStatus.OK
    
@auth_api.route('/notification')
@auth_api.doc(description='Change notification setting of a user')
class UserNotification(Resource):
    @auth_api.expect(parsers.notification_parser)
    @auth_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @auth_api.response(HTTPStatus.OK, 'Notification setting changed', models.success_model)
    def post(self):
        args = parsers.notification_parser.parse_args()
        token = args['token']
        notification = args['notification']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        db.updateUserNotification(user.username, notification)
        return {'message': 'Notification setting changed'}, HTTPStatus.OK
    
@auth_api.route('/monitoring')
@auth_api.doc(description='Change monitoring setting of a user')
class UserMonitoring(Resource):
    @auth_api.expect(parsers.monitoring_parser)
    @auth_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @auth_api.response(HTTPStatus.OK, 'Monitoring setting changed', models.success_model)
    def post(self):
        args = parsers.monitoring_parser.parse_args()
        token = args['token']
        monitoring = args['monitoring']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        db.updateUserMonitoring(user.username, monitoring)
        return {'message': 'Monitoring setting changed'}, HTTPStatus.OK
    
@auth_api.route('/fcm')
@auth_api.doc(description='Change FCM token of a user')
class UserFCM(Resource):
    @auth_api.expect(parsers.fcm_token_parser)
    @auth_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @auth_api.response(HTTPStatus.OK, 'FCM token changed', models.success_model)
    def post(self):
        args = parsers.fcm_token_parser.parse_args()
        token = args['token']
        fcm_token = args['fcm_token']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        db.updateUserFCMToken(user.username, fcm_token)
        return {'message': 'FCM token changed'}, HTTPStatus.OK
    
@detect_api.route('/report')
@detect_api.doc(description='Report a detected action')
class Report(Resource):
    @detect_api.expect(parsers.report_parser)
    @detect_api.response(HTTPStatus.OK, 'Action reported', models.report_model)
    @detect_api.response(HTTPStatus.BAD_REQUEST, 'Error', models.error_model)
    def post(self):
        args = parsers.report_parser.parse_args()
        cameraId = args['cameraId']
        beginTime = args['beginTime']
        endTime = args['endTime']
        sensitivity = args['sensitivity']
        accuracy = args['accuracy']
        actionId = _utils.generateUUID()
        # Check if cameraId exists
        camera = db.getCamera(cameraId)
        if camera is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        user = camera.user()
        if user is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        if not user.monitoring:
            return {'error': 'User Monitoring is disabled'}, HTTPStatus.BAD_REQUEST
        if sensitivity < user.sensitivity:
            return {'error': 'Sensitivity too low'}, HTTPStatus.BAD_REQUEST
        db.insertDetectData(actionId, cameraId, beginTime, endTime, accuracy=accuracy)
        notif.onReport(user, beginTime, actionId)
        return {'actionId': actionId}, HTTPStatus.OK

@detect_api.route('/video')
@detect_api.doc(description='Upload a video of a detected action')
class UploadVideo(Resource):
    @detect_api.expect(parsers.upload_parser)
    @detect_api.response(HTTPStatus.BAD_REQUEST, 'Error', models.error_model)
    @detect_api.response(HTTPStatus.OK, 'Video uploaded', models.success_model)
    def post(self):
        args = parsers.upload_parser.parse_args()
        actionId = args['actionId']
        file = args['file']
        action = db.getDetectData(actionId)
        if action is None:
            return {'error': 'Invalid actionId'}, HTTPStatus.BAD_REQUEST
        if not isinstance(file, werkzeug.datastructures.FileStorage):
            return {'error': 'Invalid file'}, HTTPStatus.BAD_REQUEST
        file_ext = file.filename.split('.')[-1]
        if (file_ext != 'mp4'):
            return {'error': 'Invalid or not supported file type'}, HTTPStatus.BAD_REQUEST
        load_dotenv()
        save_path = os.getenv('VIDEO_SAVE_PATH')
        file.save(os.path.join(save_path, f'{actionId}.mp4'))
        
        # Create thumbnail
        thumbnail_path = os.getenv('THUMBNAIL_SAVE_PATH')
        _utils.createThumbnail(os.path.join(save_path, f'{actionId}.mp4'), os.path.join(thumbnail_path, f'{actionId}.jpg'))        
        db.updateDetectData(actionId, DSC.RECEIVED)
        return {'message': 'Video uploaded'}, HTTPStatus.OK

@detect_api.route('/getall')
@detect_api.doc(description='Get all detect data')
class GetAllDetect(Resource):
    @detect_api.expect(parsers.detect_getAll_parser)
    @detect_api.response(HTTPStatus.OK, 'Detect data', [models.detectData_model])
    @detect_api.response(HTTPStatus.BAD_REQUEST, 'Invalid cameraId', models.error_model)
    @detect_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
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
            if camera.username != user.username:
                return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        if camera is None:
            data = db.getDetectDataByUser(user.username)
        else:
            data = db.getDetectDataByCameraId(cameraId)
        result = []
        host_access = os.getenv('HOST_ACCESS')
        for d in data:
            result.append({
                'uuid': d.uuid,
                'cameraId': d.cameraId,
                'beginTime': d.beginTimeStamp,
                'endTime': d.endTimeStamp,
                'statusCode': d.status,
                'video': f'http://{host_access}/video/{d.uuid}',
                'thumbnail': f'http://{host_access}/thumbnail/{d.uuid}',
                'accuracy': d.accuracy
            })
        return result, HTTPStatus.OK
    
@detect_api.route('/get')
@detect_api.doc(description='Get a specific detect data')
class GetDetect(Resource):
    @detect_api.expect(parsers.detect_get_parser)
    @detect_api.response(HTTPStatus.OK, 'Detect data', models.detectData_model)
    @detect_api.response(HTTPStatus.BAD_REQUEST, 'Invalid actionId', models.error_model)
    @detect_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    def get(self):
        args = parsers.detect_get_parser.parse_args()
        token = args['token']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        actionId = args['actionId']
        action = db.getDetectData(actionId)
        if action is None:
            return {'error': 'Invalid actionId'}, HTTPStatus.BAD_REQUEST
        user = db.getUserByToken(token)
        host_access = os.getenv('HOST_ACCESS')
        if user.username != action.camera().username:
            return {'error': 'You do not have access to this data'}, HTTPStatus.UNAUTHORIZED
        return {
            'uuid': action.uuid,
            'cameraId': action.cameraId,
            'beginTime': action.beginTimeStamp,
            'endTime': action.endTimeStamp,
            'statusCode': action.status,
            'video': f'http://{host_access}/video/{action.uuid}',
            'thumbnail': f'http://{host_access}/thumbnail/{action.uuid}',
            'accuracy': action.accuracy
        }, HTTPStatus.OK
        
@detect_api.route('/getdetectbytime')
@detect_api.doc(description='Get detect data by time')
class GetDetectByTime(Resource):
    @detect_api.expect(parsers.detectbyTime_parser)
    @detect_api.response(HTTPStatus.OK, 'Detect data', [models.detectData_model])
    @detect_api.response(HTTPStatus.BAD_REQUEST, 'Invalid cameraId', models.error_model)
    @detect_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    def get(self):
        args = parsers.detectbyTime_parser.parse_args()
        token = args['token']
        cameraId = args['cameraId']
        beginTime = args['beginTime']
        endTime = args['endTime']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        if cameraId is not None:
            camera = db.getCamera(cameraId)
            if camera is None:
                return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
            if camera.username != user.username:
                return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
            data = db.getCameraDetectDataByTimeRange(cameraId, beginTime, endTime)
        else:
            data = db.getUserDetectDataByTimeRange(user.username, beginTime, endTime)
        result = []
        host_access = os.getenv('HOST_ACCESS')
        for d in data:
            result.append({
                'uuid': d.uuid,
                'cameraId': d.cameraId,
                'beginTime': d.beginTimeStamp,
                'endTime': d.endTimeStamp,
                'statusCode': d.status,
                'video': f'http://{host_access}/video/{d.uuid}',
                'thumbnail': f'http://{host_access}/thumbnail/{d.uuid}',
                'accuracy': d.accuracy
            })
        return result, HTTPStatus.OK
            
    
@camera_api.route('/register')
@camera_api.doc(description='Use to assign a new camera hardware with new ID and Linking Code')
class RegisterCamera(Resource):
    @camera_api.response(HTTPStatus.OK, 'Camera registered', models.register_camera_model)
    def get(self):
        cameraId = _utils.generateCameraId()
        linkingCode = _utils.generateLinkingCode()
        db.registerCamera(cameraId=cameraId, cameraName="", linkCode=linkingCode, status=CSC.NOT_LINKED)
        return {'cameraId': cameraId, 'linkingCode': linkingCode}, HTTPStatus.OK
        
@camera_api.route('/get')
@camera_api.doc(description='Get camera information')
class GetCamera(Resource):
    @camera_api.expect(parsers.camera_parser)
    @camera_api.response(HTTPStatus.OK, 'Camera information', models.camera_model)
    @camera_api.response(HTTPStatus.BAD_REQUEST, 'Invalid cameraId', models.error_model)
    @camera_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    def get(self):
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
        if camera.username != user.username:
            return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
        return {
            'cameraId': camera.camera_id,
            'name': camera.cameraName,
            'username': camera.username,
            'status': camera.status
        }, HTTPStatus.OK
    
@camera_api.route('/getall')
@camera_api.doc(description='Get all cameras that a user has access to')
class GetAllCamera(Resource):
    @camera_api.expect(parsers.token_parser)
    @camera_api.response(HTTPStatus.OK, 'Cameras', [models.camera_model])
    @camera_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    def get(self):
        args = parsers.token_parser.parse_args()
        token = args['token']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        cameras = db.getUserCameras(user.username)
        result = []
        for camera in cameras:
            result.append({
                'cameraId': camera.camera_id,
                'name': camera.cameraName,
                'username': camera.username,
                'status': camera.status
            })
        return result, HTTPStatus.OK
    
@camera_api.route('/rename')
@camera_api.doc(description='Rename a camera')
class RenameCamera(Resource):
    @camera_api.expect(parsers.rename_camera_parser)
    @camera_api.response(HTTPStatus.BAD_REQUEST, 'Invalid cameraId', models.error_model)
    @camera_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @camera_api.response(HTTPStatus.OK, 'Camera renamed', models.success_model)
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
        if user.username != camera.username:
            return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
        db.renameCamera(cameraId, name)
        return {'message': 'Camera renamed'}, HTTPStatus.OK

@camera_api.route('/delete')
@camera_api.doc(description='Delete a camera')
class DeleteCamera(Resource):
    @camera_api.expect(parsers.camera_parser)
    @camera_api.response(HTTPStatus.BAD_REQUEST, 'Invalid cameraId', models.error_model)
    @camera_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @camera_api.response(HTTPStatus.OK, 'Camera deleted', models.success_model)
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
        if user.username != camera.username:
            return {'error': 'You do not have access to this camera'}, HTTPStatus.UNAUTHORIZED
        db.deleteCamera(cameraId)
        return {'message': 'Camera deleted'}, HTTPStatus.OK
        
    
@camera_api.route('/link')
@camera_api.doc(description='Link a camera hardware with a camera ID to a user with a linking code')
class LinkCamera(Resource):
    @camera_api.expect(parsers.link_camera_parser)
    @camera_api.response(HTTPStatus.BAD_REQUEST, 'Invalid linking code', models.error_model)
    @camera_api.response(HTTPStatus.UNAUTHORIZED, 'Authentication failed', models.authenticate_fail_model)
    @camera_api.response(HTTPStatus.OK, 'Camera linked', models.success_model)
    def post(self):
        args = parsers.link_camera_parser.parse_args()
        token = args['token']
        linkingCode = args['linkingCode']
        auth = db.authenticate(token)
        if not auth:
            return {'error': 'Authentication failed'}, HTTPStatus.UNAUTHORIZED
        user = db.getUserByToken(token)
        result = db.linkCamera(user.username, linkingCode)
        if result:
            return {'message': 'Camera linked'}, HTTPStatus.OK
        return {'error': 'Invalid linking code'}, HTTPStatus.BAD_REQUEST
    
@camera_api.route('/checkstatus')
@camera_api.doc(description='Check if a camera status. Unknow: 0, Not linked: 1, Linked: 2')
class CheckCameraStatus(Resource):
    @camera_api.expect(parsers.cameraId_parser)
    @camera_api.response(HTTPStatus.BAD_REQUEST, 'Invalid cameraId', models.error_model)
    @camera_api.response(HTTPStatus.OK, 'Camera status', models.camera_statuscheck_model)
    def get(self):
        args = parsers.cameraId_parser.parse_args()
        cameraId = args['cameraId']
        camera = db.getCamera(cameraId)
        if camera is None:
            return {'error': 'Invalid cameraId'}, HTTPStatus.BAD_REQUEST
        return {'cameraId': camera.camera_id, 'status': camera.status}, HTTPStatus.OK
        