import api.v1 as v1
from flask_restx import fields

api = v1.api

login_success_model = api.model('LoginSuccess', {
    'token': fields.String(required=True, description='Token')
})

login_fail_model = api.model('LoginFail', {
    'error': fields.String(required=True, description='Error')
})

register_success_model = api.model('RegisterSuccess', {
    'message': fields.String(required=True, description='Message')
})

register_fail_model = api.model('RegisterFail', {
    'error': fields.String(required=True, description='Error')
})

authenticate_fail_model = api.model('AuthenticateFail', {
    'error': fields.String(required=True, description='Error', default='Authentication failed')
})

token_expire_model = api.model('TokenExpire', {
    'error': fields.String(required=True, description='Error', default='Token expired')
})
    