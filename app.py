from flask import Blueprint, send_file, request, Response
import os
import re
from http import HTTPStatus
from dotenv import load_dotenv
from _utils import createThumbnail

app = Blueprint('app', __name__, url_prefix='/')

@app.route('/video/<string:uuid>', methods=['GET'])
def get_video(uuid):
    load_dotenv()
    path = os.getenv('VIDEO_SAVE_PATH')
    file_name = f'{uuid}.mp4'
    file_path = os.path.join(path, file_name)
    
    if not os.path.exists(file_path):
        return 'Video not found', HTTPStatus.NOT_FOUND
    if not os.path.isfile(file_path):
        return 'Invalid video', HTTPStatus.BAD_REQUEST
    
    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(file_path, mimetype='video/mp4')
    
    size = os.path.getsize(file_path)
    byte1, byte2 = 0, None

    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        if match:
            byte1, byte2 = match.groups()
            byte1 = int(byte1)
            if byte2:
                byte2 = int(byte2)
    
    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1 + 1
    
    with open(file_path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)
    
    rv = Response(data, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)
    rv.headers.add('Content-Range', f'bytes {byte1}-{byte1 + length - 1}/{size}')
    rv.headers.add('Accept-Ranges', 'bytes')
    
    return rv

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
