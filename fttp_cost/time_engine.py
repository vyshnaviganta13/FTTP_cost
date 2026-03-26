def calculate_time_savings(distance_km):

    # Manual telecom planning (survey + approvals + estimation)
    manual_days = distance_km * 0.4   # ~0.4 day per km

    # AI system time
    ai_minutes = 1

    saved_hours = (manual_days * 24) - (ai_minutes / 60)

    return {
        "manual_days": round(manual_days, 2),
        "ai_minutes": ai_minutes,
        "time_saved_hours": round(saved_hours, 2)
    }


def budget_check(total_cost, budget=15000000):
    if total_cost <= budget:
        return "Within Budget ✅"
    else:
        return "Over Budget ⚠️"


def risk_analysis(distance_km):
    if distance_km > 20:
        return "High Risk (Long Route, permits, delays)"
    elif distance_km > 10:
        return "Medium Risk"
    else:
        return "Low Risk"


def roi_estimation(total_cost, premises=200):

    revenue_per_user = 500  # ₹ per month
    monthly_revenue = premises * revenue_per_user

    payback_months = total_cost / monthly_revenue

    return round(payback_months, 1)