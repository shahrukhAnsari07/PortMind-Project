from fastapi import APIRouter

from backend.models import (
    SimulationRequest,
    MonteCarloRequest,
)

from backend.engine.simulator import (
    run_simulation,
)

from backend.engine.monte_carlo import (
    run_monte_carlo,
)

from backend.services.ai import (
    generate_recommendation,
)


router = APIRouter(
    prefix="/api"
)


@router.get("/health")
def health():
    return {
        "status": "online",
        "service": "PortMind AI",
        "services": {
            "simulation": "online",
            "optimizer": "online",
            "ai": "online",
            "event_stream": "online",
        },
    }


@router.post("/simulate")
def simulate(
    request: SimulationRequest
):
    baseline_scenario = request.scenario.model_copy(
        update={
            "delayed_vessel": None,
            "delay_minutes": 0,
            "failed_crane": None,
            "closed_berth": None,
            "truck_shortage": 0,
            "blocked_yard": None,
            "yard_reduction_pct": 0,
            "weather": "Normal",
        }
    )

    baseline = run_simulation(
        request.vessels,
        request.resources,
        baseline_scenario,
    )

    result = run_simulation(
        request.vessels,
        request.resources,
        request.scenario,
    )

    before_wait = baseline[
        "metrics"
    ]["average_waiting"]

    after_wait = result[
        "metrics"
    ]["average_waiting"]

    comparison = {
        "average_waiting_before":
            before_wait,

        "average_waiting_after":
            after_wait,

        "waiting_reduction":
            round(
                before_wait - after_wait,
                2
            ),

        "queue_before":
            baseline["metrics"]["queue_length"],

        "queue_after":
            result["metrics"]["queue_length"],

        "cost_before":
            round(
                before_wait * 1000
                + baseline["metrics"]["queue_length"]
                * 25000,
                2
            ),

        "cost_after":
            round(
                after_wait * 1000
                + result["metrics"]["queue_length"]
                * 25000,
                2
            ),
    }

    result["baseline"] = baseline
    result["comparison"] = comparison

    return result


@router.post("/monte-carlo")
def monte_carlo(
    request: MonteCarloRequest
):
    return run_monte_carlo(
        run_simulation,
        request.simulation.vessels,
        request.simulation.resources,
        request.simulation.scenario,
        request.runs,
    )


@router.post("/ai")
def ai(
    request: SimulationRequest
):
    result = run_simulation(
        request.vessels,
        request.resources,
        request.scenario,
    )

    return generate_recommendation(
        result
    )