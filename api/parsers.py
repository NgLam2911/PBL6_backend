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

