def evaluate_iq(iq_array, detectors: dict, scoring_config: dict):
    """
    Оцінює ризик сигналу на основі результатів аналітичних модулів.

    Parameters:
        iq_array: np.ndarray
        detectors: dict з ключами: energy, phase, entropy, lte, burst
        scoring_config: конфігураційний блок 'scoring' для потоку

    Returns:
        total_score: float — сума балів
        reasons: list[str] — пояснення які модулі спрацювали
    """
    score = 0.0
    reasons = []

    def try_add(key, module):
        nonlocal score
        try:
            result = module.analyze(iq_array)
            if result:
                weight = scoring_config.get(key, 0.0)
                score += weight
                reasons.append(f"{key} (+{weight:.2f})")
        except Exception as e:
            reasons.append(f"{key} ❌ error: {e}")

    try_add("energy_deviation", detectors.get("energy"))
    try_add("phase_jitter",     detectors.get("phase"))
    try_add("entropy_detector", detectors.get("entropy"))
    try_add("lte_suppressor",   detectors.get("lte"))
    try_add("burst_detector",   detectors.get("burst"))

    # Power tracker — окрема логіка (бо не клас)
    if "power_tracker" in scoring_config:
        weight = scoring_config["power_tracker"]
        from analysis.power_tracker import analyze_power
        if analyze_power(iq_array, scoring_config.get("power_tracker_cfg", {})):
            score += weight
            reasons.append(f"power_tracker (+{weight:.2f})")

    return score, reasons