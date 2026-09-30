from typing import Dict, List, Any
import math


def _weather_multiplier(weather: str) -> float:
    normalized = (weather or "Normal").strip().lower()

    if normalized in {"heavy rain", "heavy_rain"}:
        return 1.20

    if normalized in {
        "major disruption",
        "major_disruption",
        "storm"
    }:
        return 1.40

    if normalized in {"rain", "light rain", "light_rain"}:
        return 1.10

    return 1.0


def _effective_cranes(resources, scenario):
    cranes = resources.cranes

    if cranes is None:
        cranes = max(
            1,
            min(3, resources.berths + 1)
        )

    if scenario.failed_crane is not None:
        cranes = max(0, cranes - 1)

    return cranes


def _effective_trucks(resources, scenario):
    return max(
        0,
        resources.trucks - scenario.truck_shortage
    )


def _yard_capacity_factor(scenario):
    return max(
        0.0,
        1.0 - (scenario.yard_reduction_pct / 100.0)
    )


def _processing_time(vessel, cranes, trucks, scenario):
    crane_factor = max(1, cranes)
    truck_factor = max(1, trucks)

    base = vessel.containers / crane_factor * 1.5

    truck_penalty = 1.0

    if trucks == 0:
        truck_penalty = 1.8
    elif trucks < 5:
        truck_penalty = 1.35
    elif trucks < 8:
        truck_penalty = 1.15

    weather = _weather_multiplier(
        scenario.weather
    )

    return max(
        20,
        base * truck_penalty * weather
    )


def _available_berths(resources, scenario):
    berths = list(range(1, resources.berths + 1))

    if scenario.closed_berth in berths:
        berths.remove(scenario.closed_berth)

    return berths


def _available_yards(resources, scenario):
    yards = list(range(1, resources.yards + 1))

    if scenario.blocked_yard in yards:
        yards.remove(scenario.blocked_yard)

    return yards


def _calculate_horizon(schedule):
    if not schedule:
        return 240

    return max(
        item["departure"]
        for item in schedule
    ) + 30


def _schedule_vessels(
    vessels,
    resources,
    scenario
):
    berths = _available_berths(
        resources,
        scenario
    )

    yards = _available_yards(
        resources,
        scenario
    )

    cranes = _effective_cranes(
        resources,
        scenario
    )

    trucks = _effective_trucks(
        resources,
        scenario
    )

    if not berths:
        return [], [
            {
                "type": "critical",
                "message": "All berths are unavailable."
            }
        ]

    if not yards:
        return [], [
            {
                "type": "critical",
                "message": "All yard blocks are unavailable."
            }
        ]

    berth_available = {
        berth: 0
        for berth in berths
    }

    yard_load = {
        yard: 0
        for yard in yards
    }

    schedule = []
    incidents = []

    sorted_vessels = sorted(
        vessels,
        key=lambda v: (
            v.eta,
            -v.priority
        )
    )

    for vessel in sorted_vessels:

        eta = vessel.eta

        if (
            scenario.delayed_vessel
            and vessel.id == scenario.delayed_vessel
        ):
            eta += scenario.delay_minutes

            incidents.append({
                "type": "vessel_delay",
                "vessel": vessel.name,
                "message": (
                    f"{vessel.name} delayed by "
                    f"{scenario.delay_minutes} minutes."
                )
            })

        selected_berth = min(
            berths,
            key=lambda b: berth_available[b]
        )

        berth_start = max(
            eta,
            berth_available[selected_berth]
        )

        waiting = max(
            0,
            berth_start - eta
        )

        processing = _processing_time(
            vessel,
            cranes,
            trucks,
            scenario
        )

        selected_yard = min(
            yards,
            key=lambda y: yard_load[y]
        )

        yard_factor = _yard_capacity_factor(
            scenario
        )

        effective_capacity = max(
            1,
            int(
                1000
                * yard_factor
            )
        )

        yard_load[
            selected_yard
        ] += vessel.containers

        if (
            yard_load[selected_yard]
            > effective_capacity
        ):
            incidents.append({
                "type": "yard_congestion",
                "yard": selected_yard,
                "message": (
                    f"Yard {selected_yard} "
                    "is approaching capacity."
                )
            })

        departure = (
            berth_start
            + processing
        )

        berth_available[
            selected_berth
        ] = departure

        schedule.append({
            "vessel_id": vessel.id,
            "vessel": vessel.name,
            "eta": eta,
            "berth": selected_berth,
            "yard": selected_yard,
            "containers": vessel.containers,
            "priority": vessel.priority,
            "waiting": round(waiting, 2),
            "processing": round(processing, 2),
            "start": round(berth_start, 2),
            "departure": round(departure, 2),
        })

    if scenario.failed_crane:
        incidents.append({
            "type": "crane_failure",
            "crane": scenario.failed_crane,
            "message": (
                f"Crane {scenario.failed_crane} "
                "is unavailable."
            )
        })

    if scenario.closed_berth:
        incidents.append({
            "type": "berth_closed",
            "berth": scenario.closed_berth,
            "message": (
                f"Berth {scenario.closed_berth} "
                "is closed."
            )
        })

    if scenario.truck_shortage:
        incidents.append({
            "type": "truck_shortage",
            "message": (
                f"{scenario.truck_shortage} trucks "
                "are unavailable."
            )
        })

    if scenario.blocked_yard:
        incidents.append({
            "type": "yard_blocked",
            "yard": scenario.blocked_yard,
            "message": (
                f"Yard {scenario.blocked_yard} "
                "is blocked."
            )
        })

    if scenario.yard_reduction_pct:
        incidents.append({
            "type": "yard_capacity",
            "message": (
                f"Yard capacity reduced by "
                f"{scenario.yard_reduction_pct}%."
            )
        })

    if scenario.weather != "Normal":
        incidents.append({
            "type": "weather",
            "message": (
                f"Weather condition: "
                f"{scenario.weather}."
            )
        })

    return schedule, incidents


def _metrics(schedule, resources):
    if not schedule:
        return {
            "total_vessels": 0,
            "average_waiting": 0,
            "max_waiting": 0,
            "total_containers": 0,
            "horizon": 240,
            "average_turnaround": 0,
            "throughput": 0,
            "queue_length": 0,
        }

    waits = [
        item["waiting"]
        for item in schedule
    ]

    turnaround = [
        item["departure"] - item["eta"]
        for item in schedule
    ]

    containers = sum(
        item["containers"]
        for item in schedule
    )

    horizon = _calculate_horizon(
        schedule
    )

    return {
        "total_vessels": len(schedule),
        "average_waiting": round(
            sum(waits) / len(waits),
            2
        ),
        "max_waiting": round(
            max(waits),
            2
        ),
        "total_containers": containers,
        "horizon": round(horizon, 2),
        "average_turnaround": round(
            sum(turnaround)
            / len(turnaround),
            2
        ),
        "throughput": round(
            containers / max(horizon, 1) * 60,
            2
        ),
        "queue_length": sum(
            1 for wait in waits
            if wait > 0
        ),
    }


def run_simulation(
    vessels,
    resources,
    scenario
):
    schedule, incidents = _schedule_vessels(
        vessels,
        resources,
        scenario
    )

    metrics = _metrics(
        schedule,
        resources
    )

    crane_count = _effective_cranes(
        resources,
        scenario
    )

    truck_count = _effective_trucks(
        resources,
        scenario
    )

    yard_factor = _yard_capacity_factor(
        scenario
    )

    utilization = {
        "cranes": round(
            min(
                100,
                60 + len(schedule) * 7
            ),
            2
        ),
        "trucks": round(
            min(
                100,
                45 + len(schedule) * 6
            ),
            2
        ),
        "yards": round(
            min(
                100,
                35 + len(schedule) * 8
            ) / max(
                yard_factor,
                0.1
            ),
            2
        ),
    }

    return {
        "schedule": schedule,
        "incidents": incidents,
        "metrics": metrics,
        "resources": {
            "cranes": crane_count,
            "trucks": truck_count,
            "berths": resources.berths,
            "yards": resources.yards,
        },
        "utilization": utilization,
        "scenario": {
            "weather": scenario.weather,
            "delayed_vessel": scenario.delayed_vessel,
            "delay_minutes": scenario.delay_minutes,
            "failed_crane": scenario.failed_crane,
            "closed_berth": scenario.closed_berth,
            "truck_shortage": scenario.truck_shortage,
            "blocked_yard": scenario.blocked_yard,
            "yard_reduction_pct":
                scenario.yard_reduction_pct,
        },
    }