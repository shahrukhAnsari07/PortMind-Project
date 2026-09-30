import os


def generate_recommendation(
    simulation_data
):
    metrics = simulation_data.get(
        "metrics",
        {}
    )

    incidents = simulation_data.get(
        "incidents",
        []
    )

    recommendations = []

    average_waiting = metrics.get(
        "average_waiting",
        0
    )

    queue_length = metrics.get(
        "queue_length",
        0
    )

    if average_waiting > 60:
        recommendations.append(
            "Consider adding or reallocating "
            "berth capacity to reduce vessel waiting."
        )

    if queue_length >= 2:
        recommendations.append(
            "Prioritize vessels with high ETA "
            "pressure and shorter processing times."
        )

    for incident in incidents:

        incident_type = incident.get(
            "type"
        )

        if incident_type == "crane_failure":
            recommendations.append(
                "Reassign available cranes and "
                "prioritize critical vessel operations."
            )

        elif incident_type == "berth_closed":
            recommendations.append(
                "Re-sequence vessels around the "
                "remaining available berths."
            )

        elif incident_type == "truck_shortage":
            recommendations.append(
                "Prioritize high-priority container "
                "moves while truck capacity is constrained."
            )

        elif incident_type == "yard_congestion":
            recommendations.append(
                "Redistribute containers across "
                "available yard blocks."
            )

        elif incident_type == "weather":
            recommendations.append(
                "Increase handling-time buffers "
                "while adverse weather persists."
            )

    if not recommendations:
        recommendations.append(
            "Current operating conditions are "
            "within the configured simulation limits."
        )

    return {
        "summary": (
            "AI copilot generated recommendations "
            "from the current digital-twin state."
        ),
        "recommendations": recommendations,
        "model": os.getenv(
            "AI_MODEL",
            "rule-based-copilot"
        ),
    }