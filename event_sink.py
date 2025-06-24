from collections import deque, defaultdict
from datetime import datetime

# Максимальна кількість подій у памʼяті
MAX_EVENTS = 500

# Кільцева черга з останніми тривогами
_alert_buffer = deque(maxlen=MAX_EVENTS)

# Лічильник подій по потоках (не обовʼязковий, але зручно)
_alert_counter_per_stream = defaultdict(int)

def register_alert(alert_obj: dict):
    """Реєструє новий ALERT у буфері"""
    alert_obj["id"] = len(_alert_buffer)
    if "time" not in alert_obj:
        alert_obj["time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    stream_id = alert_obj.get("stream", "unknown")
    _alert_counter_per_stream[stream_id] += 1

    _alert_buffer.append(alert_obj)

def get_alerts():
    """Повертає всі поточні ALERT'и"""
    return list(_alert_buffer)

def get_alert_count_per_stream():
    """Повертає кількість тривог по кожному потоку"""
    return dict(_alert_counter_per_stream)