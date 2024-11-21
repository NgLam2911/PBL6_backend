from flask import Flask, Blueprint, send_file
import os
from http import HTTPStatus
from dotenv import load_dotenv

app = Blueprint('app', __name__, url_prefix='/')

@app.route('/video/<string:uuid>', methods=['GET'])
def get_video(uuid):
    load_dotenv()
    path = os.getenv('VIDEO_SAVE_PATH')
    file_name = os.path.join(path, f'{uuid}.mp4')
    if not os.path.exists(file_name):
        return 'Video not found', HTTPStatus.NOT_FOUND
    if not os.path.isfile(file_name):
        return 'Invalid video', HTTPStatus.BAD_REQUEST
    return send_file(file_name, as_attachment=True, mimetype='video/mp4'), HTTPStatus.OK
