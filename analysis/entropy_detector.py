import numpy as np
from scipy.stats import entropy

class EntropyDetector:
    """
    Виявляє сигнали з ритмічною активністю або зниженням ентропії,
    характерним для структурованого (відео) потоку.
    """

    def __init__(self, bins=64, entropy_thresh=3.5):
        """
        Parameters:
            bins: кількість бінів у гістограмі амплітуд
            entropy_thresh: поріг ентропії — якщо нижче → структурований сигнал
        """
        self.bins = bins
        self.entropy_thresh = entropy_thresh

    def analyze(self, iq_array: np.ndarray) -> bool:
        """
        Аналізує ентропію амплітудного розподілу.

        Returns:
            bool — True, якщо сигнал має знижену ентропію
        """
        if len(iq_array) == 0:
            return False

        magnitudes = np.abs(iq_array)

        # Побудова гістограми
        hist, bin_edges = np.histogram(magnitudes, bins=self.bins, density=True)
        hist = hist + 1e-12  # уникнення log(0)

        # Розрахунок ентропії
        h = entropy(hist, base=2)

        if h < self.entropy_thresh:
            print(f"[📉Entropy] Ентропія сигналу знижена: H = {h:.2f} біт — можливий структурований сигнал")
            return True
        return False