from .class_pattern import Singleton

class Notificator(Singleton):
    def __init__(self):
        pass
    
    def onReport(self, user: dict, actionId: str):
        from dbs import Firebase
        firebase = Firebase()
        isNotif = user["notification"]
        if not isNotif:
            return
        fcmToken = user["fcmToken"]
        if fcmToken == "":
            return
        title = "Reported action"
        body = "Your camera has reported an action"
        firebase._send_notification(title, body, fcmToken)