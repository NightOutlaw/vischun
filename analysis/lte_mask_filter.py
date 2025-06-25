import numpy as np


class LTEBaselineSuppressor:
    """
    Пригнічує стабільний фон LTE, виявляє залишкову енергію поверх нього.
    """

    def __init__(self, smoothing=0.05, residual_thresh_db=2.0):
        """
        Parameters:
            smoothing: згладжування для оцінки базової енергії (EMA)
            residual_thresh_db: поріг залишкової потужності
        """
        self.baseline_power = None
        self.smoothing = smoothing
        self.residual_thresh_db = residual_thresh_db

    def analyze(self, iq_array: np.ndarray) -> bool:
        """
        Визначає, чи є на фоні LTE щось незвичне.

        Returns:
            bool — True, якщо поточний фрагмент перевищує baseline
        """
        if len(iq_array) == 0:
            return False

        current_power = 10 * np.log10(np.mean(np.abs(iq_array)**2) + 1e-12)

        if self.baseline_power is None:
            self.baseline_power = current_power
            return False

        # Обновлення baseline
        self.baseline_power = (1 - self.smoothing) * self.baseline_power + self.smoothing * current_power

        delta = current_power - self.baseline_power

        if delta > self.residual_thresh_db:
            print(f"[📤LTE Suppressor] Залишкова потужність перевищує baseline: Δ{delta:.2f} dB")
            return True
        return False
