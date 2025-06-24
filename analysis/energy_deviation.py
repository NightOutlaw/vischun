import numpy as np

class EnergyDeviationTracker:
    """
    Трекер адаптивної енергетичної відхилення на базі згладженого середнього.
    """

    def __init__(self, alpha=0.05, deviation_thresh_db=2.0):
        """
        Parameters:
            alpha: швидкість згладжування EMA [0.0 ... 1.0]
            deviation_thresh_db: поріг відхилення (у dB)
        """
        self.alpha = alpha
        self.deviation_thresh_db = deviation_thresh_db
        self.ema_power = None  # стан згладженого середнього

    def analyze(self, iq_array: np.ndarray) -> bool:
        """
        Аналізує IQ-масив, повертає True якщо є значне енергетичне відхилення.

        Parameters:
            iq_array: np.ndarray of complex64

        Returns:
            deviation_detected: bool
        """
        if len(iq_array) == 0:
            return False

        # Поточна енергія сигналу (у dB)
        current_power = 10 * np.log10(np.mean(np.abs(iq_array)**2) + 1e-12)

        if self.ema_power is None:
            self.ema_power = current_power
            return False

        # EMA: згладжене середнє
        self.ema_power = (1 - self.alpha) * self.ema_power + self.alpha * current_power

        delta_db = current_power - self.ema_power

        if delta_db > self.deviation_thresh_db:
            print(f"[📊EnergyDeviation] Аномальне відхилення енергії: Δ{delta_db:.2f} dB")
            return True
        return False