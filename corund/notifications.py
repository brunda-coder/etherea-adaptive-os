try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None

class NotificationManager(QObject):
    """
    Singleton for managing system notifications silently.
    Stores messages and emits signals for UI updates (Badges/Trays),
    but does NOT trigger popups.
    """
    _instance = None
    
    # Signal emitted when a new notification arrives
    notification_added = Signal()
    # Signal emitted when notifications are cleared/read
    notifications_cleared = Signal()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        if NotificationManager._instance is not None:
             raise Exception("This class is a singleton!")
        else:
             NotificationManager._instance = self
             
        self._notifications = [] # List of dicts: {title, message, timestamp, type}

    def add(self, title: str, message: str, kind: str = "info"):
        """
        Add a silent notification.
        """
        import datetime
        n = {
            "title": title,
            "message": message,
            "kind": kind,
            "timestamp": datetime.datetime.now()
        }
        self._notifications.append(n)
        print(f"[j.a.r.v.i.s] Notification: {title} - {message}")
        self.notification_added.emit()

    def get_all(self):
        """Return all notifications, newest first."""
        return list(reversed(self._notifications))

    def get_count(self):
        return len(self._notifications)

    def clear(self):
        self._notifications = []
        self.notifications_cleared.emit()
