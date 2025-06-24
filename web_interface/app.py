from flask import Flask, render_template, request, jsonify
from event_sink import get_alerts

app = Flask(__name__)

# 🔁 Поточний статус потоків (можна оновлювати із get_alerts або окремої логіки)
stream_status = {
    "Supercam": {"packets": 0, "last_seen": None},
    "ZalaOrlan": {"packets": 0, "last_seen": None},
    "Orlan": {"packets": 0, "last_seen": None}
}

# 🧠 Позначення на ALERT'и (true/false)
alert_verdicts = {}

@app.route('/')
def dashboard():
    alerts = get_alerts()
    return render_template(
        "dashboard.html",
        alerts=alerts[-100:],  # останні 100 подій
        verdicts=alert_verdicts,
        status=stream_status
    )

@app.route('/api/verdict', methods=['POST'])
def mark_verdict():
    data = request.json
    uid = data.get("id")
    verdict = data.get("verdict")
    if uid is not None:
        alert_verdicts[uid] = verdict
    return jsonify(success=True)