# в event_sink.py
from collections import deque, defaultdict
from datetime import datetime

MAX_EVENTS = 500
_alert_buffer = deque(maxlen=MAX_EVENTS)
_alert_counter_per_stream = defaultdict(int)
_last_seen_per_stream = {}             # <— зберігаємо час останнього ALERT’у

def register_alert(alert_obj: dict):
    stream = alert_obj.get("stream", "unknown")
    now = alert_obj.setdefault("time", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    _alert_counter_per_stream[stream] += 1
    _last_seen_per_stream[stream] = now
    alert_obj["id"] = len(_alert_buffer)
    _alert_buffer.append(alert_obj)

def get_alerts():
    return list(_alert_buffer)

def get_counters():
    """Повернути лічильники і часу по потоках."""
    return {
      s: {"packets": _alert_counter_per_stream.get(s, 0),
          "last_seen": _last_seen_per_stream.get(s)}
      for s in _alert_counter_per_stream.keys()
    }