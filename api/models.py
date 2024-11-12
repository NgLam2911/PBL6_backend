import api.v1 as v1
from flask_restx import fields

api = v1.api

login_success_model = api.model('LoginSuccess', {
    'token': fields.String(required=True, description='Token')
})

register_success_model = api.model('RegisterSuccess', {
    'message': fields.String(required=True, description='User registered')
})

error_model = api.model('LoginFail', {
    'error': fields.String(required=True, description='Error')
})

success_model = api.model('Success', {
    'message': fields.String(required=True, description='Infomation')
}) # Only use this model for lazy response

authenticate_fail_model = api.model('AuthenticateFail', {
    'error': fields.String(required=True, description='Error', default='Authentication failed')
})

token_expire_model = api.model('TokenExpire', {
    'error': fields.String(required=True, description='Error', default='Token expired')
})

report_model = api.model('ReportSuccess', {
    'actionId': fields.String(required=True, description='Action ID')
})

detectData_model = api.model('DetectData', {
    'uuid': fields.String(required=True, description='Action ID'),
    'cameraId': fields.String(required=True, description='Camera ID'),
    'beginTime': fields.Integer(required=True, description='Begin of reported action time in unix timestamp'),
    'endTime': fields.Integer(required=True, description='End of reported action time in unix timestamp'),
    'statusCode': fields.Integer(required=True, description='Status code')
})

register_camera_model = api.model('RegisterCamera', {
    'cameraId': fields.String(required=True, description='Camera ID'),
    'linkingCode': fields.String(required=True, description='Linking code')
})

camera_model = api.model('GetCamera', {
    'cameraId': fields.String(required=True, description='Camera ID'),
    'name': fields.String(required=True, description='Camera name'),
    'username': fields.String(required=True, description='Username'),
    'status': fields.String(required=True, description='Camera status')
})

senitivity_model = api.model('Senitivity', {
    'senitivity': fields.Integer(required=True, description='Senitivity value')
})

    