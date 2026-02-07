try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:
        pass

    def Signal(*a, **k):
        return None


class NotificationManager(QObject):
    _instance = None

    notification_added = Signal()
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
        NotificationManager._instance = self
        self._notifications = []
        self.call_me_back_enabled = True
        self.quiet_hours = (22, 7)

    def set_call_me_back(self, enabled: bool) -> None:
        self.call_me_back_enabled = bool(enabled)

    def add(self, title: str, message: str, kind: str = "info"):
        import datetime
        now = datetime.datetime.now()
        n = {"title": title, "message": message, "kind": kind, "timestamp": now}
        self._notifications.append(n)
        self._dispatch_popup(title, message)
        if self.notification_added is not None:
            self.notification_added.emit()

    def call_me_back(self, message: str = "Time to return to your focus session.") -> bool:
        import datetime
        if not self.call_me_back_enabled:
            return False
        hour = datetime.datetime.now().hour
        start, end = self.quiet_hours
        in_quiet = hour >= start or hour < end
        if in_quiet:
            return False
        self.add("Call me back", message, kind="reminder")
        return True

    def _dispatch_popup(self, title: str, message: str) -> None:
        # Best-effort OS popup, fallback to console/in-app queue.
        try:
            from plyer import notification

            notification.notify(title=title, message=message, timeout=4)
            return
        except Exception:
            pass
        print(f"[Etherea Notification] {title}: {message}")

    def get_all(self):
        return list(reversed(self._notifications))

    def get_count(self):
        return len(self._notifications)

    def clear(self):
        self._notifications = []
        if self.notifications_cleared is not None:
            self.notifications_cleared.emit()
