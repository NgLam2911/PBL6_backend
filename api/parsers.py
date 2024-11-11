import werkzeug
from flask_restx import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username')
user_parser.add_argument('password', type=str, required=True, help='Password')

report_parser = reqparse.RequestParser()
report_parser.add_argument('cameraId', type=str, required=True, help='Camera ID')
report_parser.add_argument('beginTime', type=int, required=True, help='Begin of reported action time in unix timestamp')
report_parser.add_argument('endTime', type=int, required=True, help='End of reported action time in unix timestamp')

detect_getAll_parser = reqparse.RequestParser()
detect_getAll_parser.add_argument('token', type=str, required=True, help='Authentication token')
detect_getAll_parser.add_argument('cameraId', type=str, required=False, help='Camera ID')

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

get_all_camera_parser = reqparse.RequestParser()
get_all_camera_parser.add_argument('token', type=str, required=True, help='Authentication token')

rename_camera_parser = reqparse.RequestParser()
rename_camera_parser.add_argument('token', type=str, required=True, help='Authentication token')
rename_camera_parser.add_argument('cameraId', type=str, required=True, help='Camera ID')
rename_camera_parser.add_argument('name', type=str, required=True, help='New camera name')

link_camera_parser = reqparse.RequestParser()
link_camera_parser.add_argument('token', type=str, required=True, help='Authentication token')
link_camera_parser.add_argument('linkingCode', type=str, required=True, help='Linking code')



