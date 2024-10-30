from flask import Flask
from api.v1 import v1service

app = Flask(__name__)

host = "0.0.0.0" # Open to all connections
port = 80

if __name__ == '__main__':
    app.register_blueprint(v1service)
    app.run(debug=True, host=host, port=port, use_reloader=False)