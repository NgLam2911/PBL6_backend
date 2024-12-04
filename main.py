from flask import Flask
from api import APIv1
from app import app as webapp
import dotenv
import os
from pathlib import Path
from werkzeug.middleware.proxy_fix import ProxyFix

env_path = Path(__file__).resolve().parent / '.env'
    
if not dotenv.load_dotenv(dotenv_path=env_path):
    print("No .env file found. Please create one !")
    exit(1)
    
# Create folder for saving video and thumbnail
vfolder = os.getenv('VIDEO_SAVE_PATH')
if not os.path.exists(vfolder):
    os.makedirs(vfolder)
tfolder = os.getenv('THUMBNAIL_SAVE_PATH')
if not os.path.exists(tfolder):
    os.makedirs(tfolder)

app = Flask(__name__)

host = os.getenv("HOST")
port = os.getenv("PORT")

def api_init():
    app.register_blueprint(APIv1)
    app.register_blueprint(webapp)
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    app.run(debug=True, host=host, port=port, use_reloader=False)

if __name__ == '__main__':
    api_init()