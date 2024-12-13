from _utils import Singleton
from dbs.entities import User

class Notificator(Singleton):
    def __init__(self):
        pass
    
    def onReport(self, user: User, time: int, actionId: str):
        from dbs import Firebase
        firebase = Firebase()
        if not user.notification:
            return
        fcmToken = user.fcm_token
        if fcmToken == "":
            return
        from _utils import unix2dmyhms
        time_stamp = unix2dmyhms(time)
        title = "Reported action"
        body = "ID: " + actionId + "\nTime: " + time_stamp
        firebase._send_notification(title, body, fcmToken)