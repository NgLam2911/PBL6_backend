from dbs import Firebase
from .class_pattern import Singleton

class Notificator(Singleton):
    def __init__(self):
        self.firebase = Firebase()
    
    def onReport(self, user: dict, actionId: str):
        isNotif = user["notification"]
        if not isNotif:
            return
        fcmToken = user["fcmToken"]
        if fcmToken == "":
            return
        title = "Reported action"
        body = "Your camera has reported an action"
        self.firebase._send_notification(title, body, fcmToken)