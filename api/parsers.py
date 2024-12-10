import werkzeug
from flask_restx import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username')
user_parser.add_argument('password', type=str, required=True, help='Password')

report_parser = reqparse.RequestParser()
report_parser.add_argument('cameraId', type=str, required=True, help='Camera ID')
report_parser.add_argument('beginTime', type=int, required=True, help='Begin of reported action time in unix timestamp')
report_parser.add_argument('endTime', type=int, required=True, help='End of reported action time in unix timestamp')
report_parser.add_argument('sensitivity', type=int, required=True, help='Sensitivity of detection')

detect_getAll_parser = reqparse.RequestParser()
detect_getAll_parser.add_argument('token', type=str, required=True, help='Authentication token')
detect_getAll_parser.add_argument('cameraId', type=str, required=False, help='Camera ID')

detectbyTime_parser = reqparse.RequestParser()
detectbyTime_parser.add_argument('token', type=str, required=True, help='Authentication token')
detectbyTime_parser.add_argument('cameraId', type=str, required=False, help='Camera ID')
detectbyTime_parser.add_argument('beginTime', type=int, required=True, help='Begin of reported action time in unix timestamp')
detectbyTime_parser.add_argument('endTime', type=int, required=True, help='End of reported action time in unix timestamp')

detect_get_parser = reqparse.RequestParser()
detect_get_parser.add_argument('token', type=str, required=True, help='Authentication token')
detect_get_parser.add_argument('actionId', type=str, required=True, help='UUID of action')

changepwd_parser = reqparse.RequestParser()
changepwd_parser.add_argument('username', type=str, required=True, help='Username')
changepwd_parser.add_argument('oldPassword', type=str, required=True, help='Old password')
changepwd_parser.add_argument('newPassword', type=str, required=True, help='New password')

camera_parser = reqparse.RequestParser()
camera_parser.add_argument('token', type=str, required=True, help='Authentication token')
camera_parser.add_argument('cameraId', type=str, required=True, help='Camera ID')

cameraId_parser = reqparse.RequestParser()
cameraId_parser.add_argument('cameraId', type=str, required=True, help='Camera ID')

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', type=str, required=True, help='Authentication token')

rename_camera_parser = reqparse.RequestParser()
rename_camera_parser.add_argument('token', type=str, required=True, help='Authentication token')
rename_camera_parser.add_argument('cameraId', type=str, required=True, help='Camera ID')
rename_camera_parser.add_argument('name', type=str, required=True, help='New camera name')

link_camera_parser = reqparse.RequestParser()
link_camera_parser.add_argument('token', type=str, required=True, help='Authentication token')
link_camera_parser.add_argument('linkingCode', type=str, required=True, help='Linking code')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('actionId', type=str, required=True, help='Action ID')
upload_parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True, help='Video file')

sensitivity_parser = reqparse.RequestParser()
sensitivity_parser.add_argument('token', type=str, required=True, help='Authentication token')
sensitivity_parser.add_argument('sensitivity', type=int, required=True, help='Sensitivity value')

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ('true', '1', 'yes'):
        return True
    elif value.lower() in ('false', '0', 'no'):
        return False
    else:
        raise ValueError('Boolean value expected.')

notification_parser = reqparse.RequestParser()
notification_parser.add_argument('token', type=str, required=True, help='Authentication token')
notification_parser.add_argument('notification', type=str_to_bool, required=True, help='Notification setting')

monitoring_parser = reqparse.RequestParser()
monitoring_parser.add_argument('token', type=str, required=True, help='Authentication token')
monitoring_parser.add_argument('monitoring', type=str_to_bool, required=True, help='Monitoring setting')

fcm_token_parser = reqparse.RequestParser()
fcm_token_parser.add_argument('token', type=str, required=True, help='Authentication token')
fcm_token_parser.add_argument('fcm_token', type=str, required=True, help='FCM token')




