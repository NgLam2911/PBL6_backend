from flask import Flask
from api import APIv1
from app import app as webapp
from rtmp.rtmp import loader
from command import command_thread, command_handler
import asyncio
import threading
import dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / '.env'
    
if not dotenv.load_dotenv(dotenv_path=env_path):
    print("No .env file found. Please create one !")
    exit(1)
app = Flask(__name__)

host = os.getenv("HOST")
port = os.getenv("PORT")

def api_thread():
    app.register_blueprint(APIv1)
    app.register_blueprint(webapp)
    app.run(debug=True, host=host, port=port, use_reloader=False)
    
def rtmp_thread():
    asyncio.run(loader())

if __name__ == '__main__':
    api = threading.Thread(target=api_thread)
    rtmp = threading.Thread(target=rtmp_thread)
    cmd = threading.Thread(target=command_thread)
    handler = threading.Thread(target=command_handler)
    
    api.start()
    rtmp.start()
    cmd.start()
    handler.start()
    
    try:
        api.join()
        rtmp.join()
        cmd.join()
        handler.join()
    except KeyboardInterrupt:
        print("Shutting down gracefully...")