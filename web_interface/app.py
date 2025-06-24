from flask import Flask, render_template, request, jsonify
from event_sink import get_alerts, get_counters

app = Flask(__name__)
alert_verdicts = {}

@app.route('/')
def dashboard():
    alerts = get_alerts()
    status = get_counters()      # тепер справжні дані замість хардкоду
    return render_template(
        "dashboard.html",
        alerts=alerts[-100:],
        verdicts=alert_verdicts,
        status=status
    )

alert_verdicts = {}

@app.route('/api/verdict', methods=['POST'])
def mark_verdict():
    data = request.json
    uid = data.get("id")
    verdict = data.get("verdict")
    if uid is not None:
        alert_verdicts[uid] = verdict
    return jsonify(success=True)