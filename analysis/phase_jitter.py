import numpy as np

class PhaseJitterAnalyzer:
    """
    Аналізатор нестабільності фази на основі диференційної фази та її розкиду.
    """

    def __init__(self, jitter_thresh_deg=20.0):
        """
        Parameters:
            jitter_thresh_deg: поріг дисперсії диференційної фази (в градусах)
        """
        self.jitter_thresh_deg = jitter_thresh_deg

    def analyze(self, iq_array: np.ndarray) -> bool:
        """
        Аналізує IQ масив, повертає True, якщо фаза сигналу нестабільна

        Returns:
            bool: чи перевищено поріг нестабільності
        """
        if len(iq_array) < 2:
            return False

        # Диференційна фаза між семплами
        delta_phase = np.angle(iq_array[1:] / iq_array[:-1])  # в [-π, π]
        delta_deg = np.degrees(delta_phase)

        # Розрахунок стандартного відхилення
        jitter_std = np.std(delta_deg)

        if jitter_std > self.jitter_thresh_deg:
            print(f"[🌀PhaseJitter] Надлишкова фазова нестабільність: σ = {jitter_std:.1f}°")
            return True
        return False