import numpy as np
import time

class BurstDetector:
    """
    FSM-модуль детекції burst-подій: фіксує початок, тривалість та завершення.
    """

    def __init__(self, power_thresh_db=5.0, min_duration_ms=5.0, sample_rate=1e6):
        """
        Parameters:
            power_thresh_db: поріг перевищення (у dB відносно baseline)
            min_duration_ms: мінімальна тривалість burst'а (в мілісекундах)
            sample_rate: частота дискретизації IQ (Hz)
        """
        self.power_thresh_db = power_thresh_db
        self.min_samples = int((min_duration_ms / 1000.0) * sample_rate)

        self.state = "IDLE"
        self.baseline_power_db = None
        self.current_burst = []
        self.burst_start_time = None

    def analyze(self, iq_array: np.ndarray) -> bool:
        """
        Основна логіка FSM-аналізу burst-подій.

        Returns:
            bool — True, якщо зафіксовано завершення повноцінного burst'а
        """
        if len(iq_array) == 0:
            return False

        # Поточна потужність
        power_db = 10 * np.log10(np.mean(np.abs(iq_array) ** 2) + 1e-12)

        # Ініціалізація baseline
        if self.baseline_power_db is None:
            self.baseline_power_db = power_db
            return False

        delta_db = power_db - self.baseline_power_db

        if self.state == "IDLE":
            if delta_db > self.power_thresh_db:
                self.state = "BURST"
                self.current_burst = [iq_array]
                self.burst_start_time = time.time()
        elif self.state == "BURST":
            if delta_db > self.power_thresh_db:
                self.current_burst.append(iq_array)
            else:
                total_samples = sum(len(chunk) for chunk in self.current_burst)
                if total_samples >= self.min_samples:
                    duration_ms = (time.time() - self.burst_start_time) * 1000
                    print(f"[📛BurstDetector] Зафіксовано burst: {total_samples} семплів ≈ {duration_ms:.1f} мс")
                    self._reset()
                    return True
                self._reset()
        return False

    def _reset(self):
        self.state = "IDLE"
        self.current_burst = []
        self.burst_start_time = None