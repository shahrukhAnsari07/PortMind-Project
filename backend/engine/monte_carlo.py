import random


def run_monte_carlo(
    simulation_runner,
    vessels,
    resources,
    scenario,
    runs=100
):
    waiting_values = []
    queue_values = []
    cost_values = []

    for _ in range(runs):

        variation = random.uniform(
            0.90,
            1.10
        )

        result = simulation_runner(
            vessels,
            resources,
            scenario
        )

        average_waiting = (
            result["metrics"]["average_waiting"]
            * variation
        )

        queue = (
            result["metrics"]["queue_length"]
        )

        cost = (
            average_waiting * 1000
            + queue * 25000
        )

        waiting_values.append(
            average_waiting
        )

        queue_values.append(queue)
        cost_values.append(cost)

    waiting_values.sort()

    p50_index = int(
        len(waiting_values) * 0.50
    )

    p90_index = int(
        len(waiting_values) * 0.90
    )

    return {
        "runs": runs,
        "average_waiting": round(
            sum(waiting_values)
            / len(waiting_values),
            2
        ),
        "p50_waiting": round(
            waiting_values[
                min(
                    p50_index,
                    len(waiting_values) - 1
                )
            ],
            2
        ),
        "p90_waiting": round(
            waiting_values[
                min(
                    p90_index,
                    len(waiting_values) - 1
                )
            ],
            2
        ),
        "max_waiting": round(
            max(waiting_values),
            2
        ),
        "average_queue": round(
            sum(queue_values)
            / len(queue_values),
            2
        ),
        "average_cost": round(
            sum(cost_values)
            / len(cost_values),
            2
        ),
    }