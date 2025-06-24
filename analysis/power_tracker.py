import numpy as np

# 💡 Функція без класу — повертає True/False
def analyze_power(iq_array: np.ndarray, config: dict) -> bool:
    """
    Аналіз потужності сигналу на вікні.

    Parameters:
        iq_array: масив комплексних семплів
        config: dict з ключами 'window_size' і 'threshold_db'

    Returns:
        bool — True, якщо виявлена потужність перевищує поріг
    """
    window_size = config.get("window_size", 256)
    threshold_db = config.get("threshold_db", 2.0)

    if len(iq_array) < window_size:
        return False

    window = iq_array[:window_size]
    power_db = 10 * np.log10(np.mean(np.abs(window) ** 2) + 1e-12)

    if power_db > threshold_db:
        print(f"[📈PowerTracker] Потужність: {power_db:.2f} dB > {threshold_db:.2f} → спрацювання")
        return True

    return False