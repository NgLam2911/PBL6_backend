from flask import Flask
from api import APIv1
from rtmp.rtmp import loader
from command import command_thread, command_handler
import asyncio
import threading

app = Flask(__name__)

host = "0.0.0.0" # Open to all connections
port = 80

def api_thread():
    app.register_blueprint(APIv1)
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