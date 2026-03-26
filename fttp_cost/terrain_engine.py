def detect_terrain(route_km):

    # simple logic (can upgrade later with GIS)
    if route_km > 20:
        return "Highway / Intercity"
    elif route_km > 10:
        return "Semi-Urban"
    else:
        return "Urban"


def adjust_cost_by_terrain(cost, terrain):

    factor = 1.0

    if terrain == "Urban":
        factor = 1.2
    elif terrain == "Semi-Urban":
        factor = 1.0
    elif terrain == "Highway / Intercity":
        factor = 1.3

    adjusted_total = cost * factor

    return round(adjusted_total, 2), factor