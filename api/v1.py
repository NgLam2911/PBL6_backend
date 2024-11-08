from flask import Blueprint
from flask_restx import Api, Resource, fields
from dbs import Database
import api.parsers as parsers
import _utils
from constant import ApiRequestStatusCode as ARSC

v1service = Blueprint('api/v1', __name__, url_prefix='/api/v1')
api = Api(v1service, version='0.0.1', title='V1 API', description='Indev API')
import api.models as models
db = Database()

auth_api = api.namespace('auth', description='Auth operations')
detect_api = api.namespace('detect', description='Detect operations')

@auth_api.route('/login')
@auth_api.doc(description='Login to the system, return a token')
class Login(Resource):
    @auth_api.expect(parsers.user_parser)
    @auth_api.marshal_with(models.login_success_model, code=ARSC.SUCCESS)
    @auth_api.marshal_with(models.error_model, code=ARSC.BAD_REQUEST)
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
            return {'token': token}, ARSC.SUCCESS
        return {'error': 'Invalid username or password'}, ARSC.BAD_REQUEST
    
@auth_api.route('/register')
@auth_api.doc(description='Register a new user')
class Register(Resource):
    @auth_api.expect(parsers.user_parser)
    @auth_api.marshal_with(models.register_success_model, code=ARSC.SUCCESS)
    @auth_api.marshal_with(models.error_model, code=ARSC.BAD_REQUEST)
    def post(self):
        args = parsers.user_parser.parse_args()
        username = args['username']
        password = args['password']
        check = db.getUser(username)
        if len(check) > 0:
            return {'error': 'Username already exists'}, ARSC.BAD_REQUEST
        result = db.createUser(username, password)
        if result:
            return {'message': 'User registered'}, ARSC.SUCCESS
        return {'error': 'Username already exists'}, ARSC.BAD_REQUEST
    

@detect_api.route('/report')
class Report(Resource):
    @detect_api.expect(parsers.report_parser)
    @detect_api.marshal_with(models.report_model, code=ARSC.SUCCESS)
    @detect_api.marshal_with(models.error_model, code=ARSC.BAD_REQUEST)
    def post(self):
        args = parsers.report_parser.parse_args()
        cameraId = args['cameraId']
        beginTime = args['beginTime']
        endTime = args['endTime']
        actionId = _utils.generateUUID()
        # Check if cameraId exists
        camera = db.getCamera(cameraId)
        if len(camera) == 0:
            return {'error': 'Invalid cameraId'}, ARSC.BAD_REQUEST
        db.insertDetectData(actionId, cameraId, beginTime, endTime)
        return {'actionId': actionId}, ARSC.SUCCESS
    
@detect_api.route('/getall')
class GetAllDetect(Resource):
    @detect_api.expect(parsers.detect_getAll_parser)
    @detect_api.marshal_with(models.error_model, code=ARSC.BAD_REQUEST)
    @detect_api.marshal_with(models.authenticate_fail_model, code=ARSC.UNAUTHORIZED)
    @detect_api.marshal_with([models.detectData_model], code=ARSC.SUCCESS)
    def get(self):
        args = parsers.detect_getAll_parser.parse_args()
        token = args['token']
        user = db.loginByToken(token)
        if len(user) == 0:
            return {'error': 'Authentication failed'}, ARSC.UNAUTHORIZED
        pass
        cameraId = args['cameraId']
        camera = None
        if cameraId is not None:
            camera = db.getCamera(cameraId)
            if len(camera) == 0:
                return {'error': 'Invalid cameraId'}, ARSC.BAD_REQUEST
            userCam = db.getUserCameras(user[0]['username'])
            if camera[0]['cameraId'] not in [c['cameraId'] for c in userCam]:
                return {'error': "This user doesn't have permission to access this camera"}, ARSC.UNAUTHORIZED
        if camera is None:
            data = db.getDetectDataByUser(user[0]['username'])
        else:
            data = db.getDetectDataByCameraId(cameraId)
        return data, ARSC.SUCCESS
    
@detect_api.route('/get')
class GetDetect(Resource):
    @detect_api.expect(parsers.detect_get_parser)
    @detect_api.marshal_with(models.error_model, code=ARSC.BAD_REQUEST)
    @detect_api.marshal_with(models.authenticate_fail_model, code=ARSC.UNAUTHORIZED)
    @detect_api.marshal_with(models.detectData_model, code=ARSC.SUCCESS)
    def get(self):
        args = parsers.detect_get_parser.parse_args()
        token = args['token']
        user = db.loginByToken(token)
        if len(user) == 0:
            return {'error': 'Authentication failed'}, ARSC.UNAUTHORIZED
        actionId = args['actionId']
        data = db.getDetectData(actionId)
        if len(data) == 0:
            return {'error': 'Action not found'}, ARSC.BAD_REQUEST
        return data[0], ARSC.SUCCESS
        



