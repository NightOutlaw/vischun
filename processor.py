import numpy as np
from event_sink import register_alert
from datetime import datetime
import pytz

from analysis.power_tracker import analyze_power
from analysis.energy_deviation import EnergyDeviationTracker
from analysis.phase_jitter import PhaseJitterAnalyzer
from analysis.entropy_detector import EntropyDetector
from analysis.lte_mask_filter import LTEBaselineSuppressor
from analysis.burst_detector import BurstDetector
from score_engine import evaluate_iq

_active_analysers = {}

# Отримати поточний час в часовому поясі "Europe/Kiev"
kiev_timezone = pytz.timezone("Europe/Kiev")


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

    if stream_id not in _active_analysers:
        _active_analysers[stream_id] = {
            "energy": EnergyDeviationTracker(**config.get("energy_deviation", {})),
            "phase": PhaseJitterAnalyzer(**config.get("phase_jitter", {})),
            "entropy": EntropyDetector(**config.get("entropy_detector", {})),
            "lte": LTEBaselineSuppressor(**config.get("lte_suppressor", {})),
            "burst": BurstDetector(**config.get("burst_detector", {})),
        }

    detectors = _active_analysers[stream_id]

    analyze_power(iq, config.get("power_tracker", {}))
    detectors["energy"].analyze(iq)
    detectors["phase"].analyze(iq)
    detectors["entropy"].analyze(iq)
    detectors["lte"].analyze(iq)
    detectors["burst"].analyze(iq)

    scoring_cfg = config.get("scoring", {})
    score, reasons = evaluate_iq(iq, detectors, scoring_cfg)
    threshold = scoring_cfg.get("alert_threshold", 0.6)

    if score >= threshold:
        start_frequency = json_obj.get("startFrequency", 0)
        end_frequency = json_obj.get("endFrequency", 0)
        frequency = end_frequency - start_frequency
        alert = {
            "stream": stream_id,
            "frequency": frequency,
            "score": round(score, 2),
            "reasons": reasons,
            "time": datetime.now(kiev_timezone).strftime("%Y-%m-%d %H:%M:%S")
        }
        register_alert(alert)
        print(f"\n[🚨 ALERT] {stream_id} | {frequency/1e6:.2f} MHz | Score: {score:.2f}")
        print(f"📌 Причини: {', '.join(reasons)}\n")
