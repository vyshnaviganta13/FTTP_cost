def compute_confidence(route_km, memory_hits):

    score = 0

    if route_km > 0:
        score += 40

    if memory_hits:
        score += 30

    if route_km < 1:
        score -= 10

    if score > 60:
        return "HIGH"
    elif score > 30:
        return "MEDIUM"
    else:
        return "LOW"