from flask import Blueprint
from flask_restx import Api, Resource, fields

v1service = Blueprint('api/v1', __name__, url_prefix='/api/v1')
api = Api(v1service, version='0.0.1', title='V1 API', description='Indev API')

