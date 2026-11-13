import time
import threading
from utils.helpers import play_alarm_sound
from config import ALARM_COOLDOWN


class AlarmManager:

    def __init__(self, cooldown=ALARM_COOLDOWN):
        self.cooldown = cooldown
        self.last_alarm_time = 0
        self.is_playing = False

    def trigger_alarm(self, freq=1200, duration=350):
        now = time.time()
        if now - self.last_alarm_time < self.cooldown or self.is_playing:
            return

        self.last_alarm_time = now
        self.is_playing = True

        def _play():
            play_alarm_sound(freq, duration)
            self.is_playing = False

        thread = threading.Thread(target=_play, daemon=True)
        thread.start()
