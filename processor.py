import numpy as np
from event_sink import register_alert
from datetime import datetime

# Аналітичні модулі
from analysis.power_tracker import analyze_power
from analysis.energy_deviation import EnergyDeviationTracker
from analysis.phase_jitter import PhaseJitterAnalyzer
from analysis.entropy_detector import EntropyDetector
from analysis.lte_mask_filter import LTEBaselineSuppressor
from analysis.burst_detector import BurstDetector

# Бальна модель
from score_engine import evaluate_iq

# Стани по потоках
_active_analysers = {}

def decode_samples(samples):
    if not samples or len(samples) % 2 != 0:
        print("⚠️ Некоректний масив IQ")
        return None
    return np.array(samples, dtype=np.float32).view(np.complex64)

def process_iq_packet(json_obj, config: dict, stream_id: str):
    if not config or json_obj.get("payload") != "iq":
        return

    iq = decode_samples(json_obj.get("samples"))
    if iq is None:
        return

    # ініціалізація детекторів для потоку
    if stream_id not in _active_analysers:
        _active_analysers[stream_id] = {
            "energy": EnergyDeviationTracker(**config.get("energy_deviation", {})),
            "phase": PhaseJitterAnalyzer(**config.get("phase_jitter", {})),
            "entropy": EntropyDetector(**config.get("entropy_detector", {})),
            "lte": LTEBaselineSuppressor(**config.get("lte_suppressor", {})),
            "burst": BurstDetector(**config.get("burst_detector", {})),
        }

    detectors = _active_analysers[stream_id]

    # 1️⃣ Power tracker (функціональний)
    analyze_power(iq, config.get("power_tracker", {}))

    # 2️⃣ Решта модулів (стано-залежні)
    detectors["energy"].analyze(iq)
    detectors["phase"].analyze(iq)
    detectors["entropy"].analyze(iq)
    detectors["lte"].analyze(iq)
    detectors["burst"].analyze(iq)

    # 🎯 Сумарна оцінка
    scoring_cfg = config.get("scoring", {})
    score, reasons = evaluate_iq(iq, detectors, scoring_cfg)
    threshold = scoring_cfg.get("alert_threshold", 0.6)

    if score >= threshold:
        frequency = json_obj.get("frequency", 0)
        alert = {
            "stream": stream_id,
            "frequency": frequency,
            "score": round(score, 2),
            "reasons": reasons,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        register_alert(alert)

        print(f"\n[🚨 ALERT] {stream_id} | {frequency/1e6:.2f} MHz | Score: {score:.2f}")
        print(f"📌 Причини: {', '.join(reasons)}\n")