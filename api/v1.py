from flask import Blueprint
from flask_restx import Api, Resource, fields
from dbs import Database
import api.parsers as parsers
import _utils
from constant import ApiRequestStatusCode as ARSC

v1service = Blueprint('api/v1', __name__, url_prefix='/api/v1')
api = Api(v1service, version='0.0.1', title='V1 API', description='Indev API')
import models
db = Database()

auth_api = api.namespace('auth', description='Auth operations')
detect_api = api.namespace('detect', description='Detect operations')

@auth_api.route('/login')
@auth_api.doc(description='Login to the system, return a token')
class Login(Resource):
    @auth_api.expect(parsers.login_parser)
    @auth_api.marshal_with(models.login_success_model, code=ARSC.SUCCESS)
    @auth_api.marshal_with(models.login_fail_model, code=ARSC.BAD_REQUEST)
    def post(self):
        args = parsers.login_parser.parse_args()
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



