from _utils import Singleton

class Notificator(Singleton):
    def __init__(self):
        pass
    
    def onReport(self, user: dict, time: int):
        from dbs import Firebase
        firebase = Firebase()
        isNotif = user["notification"]
        if not isNotif:
            return
        fcmToken = user["fcm_token"]
        if fcmToken == "":
            return
        from _utils import unix2dmyhms
        time_stamp = unix2dmyhms(time)
        title = "Reported action"
        body = "Your camera has reported an action at " + time_stamp
        firebase._send_notification(title, body, fcmToken)