def compare_scenarios(distance, rates):

    underground = rates["civil_per_km"] * distance
    aerial = underground * 0.6
    duct_reuse = underground * 0.4

    scenarios = {
        "underground": underground,
        "aerial": aerial,
        "duct_reuse": duct_reuse
    }

    best = min(scenarios, key=scenarios.get)

    return scenarios, best