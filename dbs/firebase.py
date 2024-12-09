import firebase_admin
from firebase_admin import credentials, messaging
from _utils import Singleton
from dotenv import load_dotenv
import os

class Firebase(Singleton):
    app: firebase_admin.App = None
    
    def __init__(self):
        if not firebase_admin._apps:
            load_dotenv()
            cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIAL"))
            self.app = firebase_admin.initialize_app(cred)
        else:
            self.app = firebase_admin.get_app()
    
    def _send_notification(self, title: str, body: str, fcm_token: str):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=fcm_token,
        )

        try:
            _ = messaging.send(message=message, app=self.app)
        except Exception as e:
            print("Error when sending notification:", e)
        pass
    