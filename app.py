from flask import Flask, Blueprint, send_file, send_from_directory
import os
from http import HTTPStatus
from dotenv import load_dotenv
from _utils import createThumbnail

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
    return send_from_directory(path, file_name, mimetype='video/mp4'), HTTPStatus.OK

@app.route('/thumbnail/<string:uuid>', methods=['GET'])
def get_thumbnail(uuid):
    load_dotenv()
    path = os.getenv('THUMBNAIL_SAVE_PATH')
    file_name = os.path.join(path, f'{uuid}.jpg')
    if not os.path.exists(file_name):
        # Check if the video exists but thumbnail not found
        video_path = os.path.join(os.getenv('VIDEO_SAVE_PATH'), f'{uuid}.mp4')
        if os.path.exists(video_path):
            createThumbnail(video_path, file_name)
            return send_file(file_name, mimetype='image/jpg'), HTTPStatus.OK
        else:
            return 'Thumbnail not found', HTTPStatus.NOT_FOUND
    if not os.path.isfile(file_name):
        return 'Invalid thumbnail', HTTPStatus.BAD_REQUEST
    return send_file(file_name, mimetype='image/jpg'), HTTPStatus.OK
