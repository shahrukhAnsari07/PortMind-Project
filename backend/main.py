from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import random
import math

app = FastAPI(title="PortMind AI", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DEFAULT_VESSELS = [
    {"name": "Ocean Star", "arrival_time": 0, "service_time": 150, "containers": 300, "priority": 2},
    {"name": "Blue Horizon", "arrival_time": 35, "service_time": 120, "containers": 240, "priority": 1},
    {"name": "Pacific Dawn", "arrival_time": 70, "service_time": 110, "containers": 220, "priority": 2},
    {"name": "Evergreen", "arrival_time": 100, "service_time": 90, "containers": 180, "priority": 1},
    {"name": "Maersk Nova", "arrival_time": 140, "service_time": 130, "containers": 260, "priority": 2},
    {"name": "Atlas Voyager", "arrival_time": 185, "service_time": 105, "containers": 210, "priority": 3},
    {"name": "Indian Ocean", "arrival_time": 225, "service_time": 95, "containers": 190, "priority": 2},
    {"name": "Harbor Queen", "arrival_time": 270, "service_time": 80, "containers": 160, "priority": 1},
]

SCENARIO_PRESETS = {
    "normal": {"label": "Normal operations", "weather_factor": 1.0, "extra_delay": 0, "truck_delta": 0, "yard_factor": 1.0},
    "vessel_delay": {"label": "+30 min vessel delay", "weather_factor": 1.0, "extra_delay": 30, "truck_delta": 0, "yard_factor": 1.0},
    "crane_failure": {"label": "Crane failure", "weather_factor": 1.0, "extra_delay": 0, "truck_delta": 0, "yard_factor": 1.0},
    "heavy_rain": {"label": "Heavy rain", "weather_factor": 1.25, "extra_delay": 15, "truck_delta": 0, "yard_factor": 1.0},
    "truck_shortage": {"label": "Truck shortage", "weather_factor": 1.0, "extra_delay": 0, "truck_delta": -2, "yard_factor": 1.0},
    "yard_congestion": {"label": "Yard congestion", "weather_factor": 1.0, "extra_delay": 0, "truck_delta": 0, "yard_factor": 0.65},
    "major_disruption": {"label": "Major disruption", "weather_factor": 1.35, "extra_delay": 45, "truck_delta": -3, "yard_factor": 0.55},
}

class VesselInput(BaseModel):
    name: str
    arrival_time: float = Field(ge=0)
    service_time: float = Field(gt=0)
    containers: int = Field(default=200, ge=1)
    priority: int = Field(default=2, ge=1, le=3)

class Resources(BaseModel):
    vessels: int = Field(default=4, ge=1, le=20)
    berths: int = Field(default=2, ge=1, le=10)
    cranes: Optional[int] = Field(default=None, ge=1, le=20)
    trucks: int = Field(default=12, ge=1, le=100)
    yards: int = Field(default=4, ge=1, le=30)

class Scenario(BaseModel):
    delayed_vessel: Optional[str] = None
    delay_minutes: float = Field(default=0, ge=0, le=1440)
    failed_crane: Optional[int] = None
    weather: str = "normal"
    truck_delta: int = 0
    yard_capacity_factor: float = Field(default=1.0, ge=0.2, le=1.0)
    scenario_name: str = "normal"
    closed_berth: Optional[int] = Field(default=None, ge=1, le=10)
    truck_shortage: int = Field(default=0, ge=0, le=100)
    blocked_yard: Optional[int] = Field(default=None, ge=1, le=30)
    yard_reduction_pct: float = Field(default=0, ge=0, le=100)
    resources: Resources = Field(default_factory=Resources)
    vessels: Optional[List[VesselInput]] = None


def active_vessels(req: Scenario):
    if req.vessels:
        return [v.model_dump() for v in req.vessels[: req.resources.vessels]]
    return DEFAULT_VESSELS[: req.resources.vessels]


def auto_cranes(vessel_count: int, requested: Optional[int]):
    if requested is not None:
        return requested
    return max(1, min(8, math.ceil(vessel_count * 0.75)))


def apply_scenario(vessels, req: Scenario):
    cfg = SCENARIO_PRESETS.get(req.scenario_name, SCENARIO_PRESETS["normal"])
    weather = req.weather if str(req.weather).strip().lower() != "normal" else req.scenario_name
    weather_key = str(weather).strip().lower().replace(" ", "_")
    factor = cfg["weather_factor"] if weather_key in ("heavy_rain", "major_disruption", "storm") else 1.0
    extra = cfg["extra_delay"] if req.scenario_name != "normal" else 0
    if req.scenario_name == "major_disruption":
        extra = 45
    if req.scenario_name == "vessel_delay" and not req.delayed_vessel:
        extra = 30
    result = []
    for v in vessels:
        item = dict(v)
        if req.delayed_vessel and item["name"] == req.delayed_vessel:
            item["arrival_time"] += req.delay_minutes
        if extra and (req.scenario_name == "major_disruption" or item["name"] == req.delayed_vessel):
            item["arrival_time"] += extra
        item["service_time"] *= factor
        result.append(item)
    return result


def schedule(req: Scenario):
    raw = active_vessels(req)
    vessels = apply_scenario(raw, req)
    crane_count = auto_cranes(len(vessels), req.resources.cranes)
    trucks = max(1, req.resources.trucks + req.truck_delta + SCENARIO_PRESETS.get(req.scenario_name, {}).get("truck_delta", 0) - req.truck_shortage)
    effective_yard_factor = (req.yard_capacity_factor if req.yard_capacity_factor else 1.0) * (1 - req.yard_reduction_pct / 100)
    yard_capacity = max(1, int(req.resources.yards * max(0.2, effective_yard_factor) * 100))
    failed = req.failed_crane
    available_cranes = [i for i in range(1, crane_count + 1) if i != failed]
    available_berths = [i for i in range(req.resources.berths) if i + 1 != req.closed_berth]
    if not available_berths:
        available_berths = [0]
    if not available_cranes:
        available_cranes = [1]
        crane_count = 1

    berth_free = [0.0] * req.resources.berths
    crane_free = {c: 0.0 for c in available_cranes}
    truck_free = [0.0] * trucks
    yard_free = [0.0] * req.resources.yards
    truck_intervals = []
    crane_intervals = []
    yard_intervals = []
    rows = []
    events = []

    ordered = sorted(vessels, key=lambda x: (x["arrival_time"], x.get("priority", 2)))
    for idx, v in enumerate(ordered):
        arrival = float(v["arrival_time"])
        service = float(v["service_time"])
        berth = min(available_berths, key=lambda i: berth_free[i])
        crane = min(available_cranes, key=lambda c: crane_free[c])
        truck = min(range(len(truck_free)), key=lambda i: truck_free[i])
        yard_candidates = [i for i in range(len(yard_free)) if i + 1 != req.blocked_yard]
        if not yard_candidates:
            yard_candidates = [0]
        yard = min(yard_candidates, key=lambda i: yard_free[i])
        start = max(arrival, berth_free[berth], crane_free[crane], truck_free[truck], yard_free[yard])
        finish = start + service
        wait = max(0, start - arrival)
        berth_free[berth] = finish
        crane_free[crane] = finish
        truck_free[truck] = finish
        yard_free[yard] = finish
        crane_intervals.append((start, finish, crane, v["name"]))
        truck_intervals.append((start, finish, truck + 1, v["name"]))
        yard_intervals.append((start, finish, yard + 1, v["name"]))
        rows.append({
            "vessel": v["name"], "arrival_time": arrival, "berth": berth + 1, "crane": crane,
            "truck": truck + 1, "yard": yard + 1, "start_time": start, "end_time": finish,
            "waiting_time": wait, "service_time": service, "containers": v.get("containers", 200),
            "priority": v.get("priority", 2),
        })
        events.append({"time": start, "type": "operation", "message": f"{v['name']} starts at Berth {berth+1} with Crane {crane}."})
        if wait > 0:
            events.append({"time": arrival, "type": "warning", "message": f"{v['name']} waits {round(wait)} min for resources."})

    horizon = max([r["end_time"] for r in rows], default=0)
    total_crane_capacity = max(1, crane_count * horizon)
    crane_busy = sum(r["service_time"] for r in rows)
    crane_util = min(100, crane_busy / total_crane_capacity * 100)
    peak = 0
    for t in sorted(set([x for a,b,_,_ in crane_intervals for x in (a,b)])):
        active = sum(1 for a,b,_,_ in crane_intervals if a <= t < b)
        peak = max(peak, active)
    truck_busy = sum(r["service_time"] for r in rows)
    truck_util = min(100, truck_busy / max(1, trucks * horizon) * 100)
    yard_util = min(100, sum(r["containers"] for r in rows) / max(1, yard_capacity * len(rows)) * 100)
    avg_wait = sum(r["waiting_time"] for r in rows) / max(1, len(rows))
    waiting = sum(1 for r in rows if r["waiting_time"] > 0)
    berth_util = min(100, sum(r["service_time"] for r in rows) / max(1, req.resources.berths * horizon) * 100)
    throughput = sum(r["containers"] for r in rows) / max(1, horizon) * 60
    idle_crane = max(0, 100 - crane_util)

    # Simple transparent cost assumptions for demo purposes.
    waiting_cost = sum(r["waiting_time"] for r in rows) * 1200
    crane_idle_cost = (idle_crane / 100) * crane_count * horizon * 450
    truck_idle_cost = ((100 - truck_util) / 100) * trucks * horizon * 120
    total_cost = waiting_cost + crane_idle_cost + truck_idle_cost

    incidents = []
    if failed:
        incidents.append({"severity": "high", "title": f"Crane {failed} failure", "detail": "Affected crane removed from active assignment; remaining capacity is used for rescheduling."})
    if req.delayed_vessel and req.delay_minutes > 0:
        incidents.append({"severity": "medium", "title": f"{req.delayed_vessel} delayed", "detail": f"Arrival shifted by {round(req.delay_minutes)} min."})
    if req.scenario_name in ("heavy_rain", "major_disruption"):
        incidents.append({"severity": "medium", "title": "Weather degradation", "detail": "Service productivity reduced by the selected weather factor."})
    if truck_delta := req.truck_delta + SCENARIO_PRESETS.get(req.scenario_name, {}).get("truck_delta", 0) - req.truck_shortage:
        if truck_delta < 0:
            incidents.append({"severity": "medium", "title": "Truck shortage", "detail": f"{abs(truck_delta)} trucks removed from the fleet."})
    if req.closed_berth:
        incidents.append({"severity": "medium", "title": f"Berth {req.closed_berth} closed", "detail": "The closed berth is excluded from new assignments."})
    if req.blocked_yard:
        incidents.append({"severity": "medium", "title": f"Yard {req.blocked_yard} blocked", "detail": "The blocked yard is excluded from new assignments."})
    if req.yard_reduction_pct > 0:
        incidents.append({"severity": "medium", "title": "Yard capacity reduced", "detail": f"Effective yard capacity reduced by {req.yard_reduction_pct:.0f}%."})

    activities = [
        f"Digital twin loaded: {req.resources.berths} berths, {crane_count} cranes, {trucks} trucks, {req.resources.yards} container yards and {len(rows)} vessels.",
        f"Crane count {'automatically calculated' if req.resources.cranes is None else 'manually configured'} as {crane_count}.",
    ]
    if failed:
        activities.append(f"Crane {failed} marked unavailable and excluded from assignments.")
    for r in rows:
        activities.append(f"{r['vessel']} starts at Berth {r['berth']} at minute {round(r['start_time'])}.")

    return {
        "resources": {"berths": req.resources.berths, "cranes": crane_count, "active_cranes": len(available_cranes), "trucks": trucks, "yards": req.resources.yards, "vessels": len(rows)},
        "schedule": rows,
        "metrics": {
            "average_waiting": avg_wait, "queue": waiting, "crane_utilization": crane_util,
            "truck_utilization": truck_util, "yard_utilization": yard_util, "peak_crane_usage": peak,
            "berth_utilization": berth_util, "throughput": throughput, "horizon": horizon,
            "crane_idle": idle_crane, "total_cost": total_cost, "waiting_cost": waiting_cost,
            "crane_idle_cost": crane_idle_cost, "truck_idle_cost": truck_idle_cost,
        },
        "incidents": incidents,
        "activities": activities,
        "events": sorted(events, key=lambda x: x["time"]),
        "timeline": rows,
        "assumptions": {"waiting_cost_per_min": 1200, "crane_idle_cost_rate": 450, "truck_idle_cost_rate": 120, "yard_capacity_units": yard_capacity},
        "scenario": {"name": req.scenario_name, "weather": req.weather, "failed_crane": failed, "delayed_vessel": req.delayed_vessel, "delay_minutes": req.delay_minutes, "closed_berth": req.closed_berth, "blocked_yard": req.blocked_yard, "truck_shortage": req.truck_shortage, "yard_reduction_pct": req.yard_reduction_pct},
    }


def make_request(req: Scenario):
    return req

@app.get("/api/health")
def health():
    return {"status": "online", "service": "PortMind AI", "time": datetime.now().isoformat(), "services": {"simulation": "online", "optimizer": "online", "ai": "online", "event_stream": "online"}}

@app.post("/api/simulate")
def simulate(req: Scenario):
    result = schedule(req)
    # Baseline is the same resources with no disruption, enabling before/after comparison.
    base = Scenario(resources=req.resources, vessels=req.vessels, scenario_name="normal", weather="normal")
    baseline = schedule(base)
    result["baseline"] = baseline
    bm, am = baseline["metrics"], result["metrics"]
    result["comparison"] = {
        "average_waiting_before": bm["average_waiting"],
        "average_waiting_after": am["average_waiting"],
        "waiting_reduction": bm["average_waiting"] - am["average_waiting"],
        "queue_before": bm["queue"], "queue_after": am["queue"],
        "cost_before": bm["total_cost"], "cost_after": am["total_cost"]
    }
    return result

@app.post("/api/reset")
def reset():
    req = Scenario(resources=Resources(vessels=4, berths=2, cranes=None, trucks=12, yards=4))
    return simulate(req)

@app.post("/api/ai")
def ai(req: dict):
    message = str(req.get("message", "")).lower()
    data = req.get("simulation") or {}
    m = data.get("metrics", {})
    sched = data.get("schedule", [])
    if "crane" in message and ("fail" in message or "remove" in message):
        text = f"A crane failure reduces available lifting capacity. Current crane usage is {m.get('crane_utilization',0):.1f}% and peak simultaneous usage is {m.get('peak_crane_usage',0)} cranes. Reassignment should prioritize the vessels with the highest waiting impact."
    elif "delay" in message or "impact" in message:
        worst = max(sched, key=lambda x: x.get("waiting_time", 0), default=None)
        text = f"The current average waiting time is {m.get('average_waiting',0):.1f} min. {worst['vessel']} has the largest individual wait at {worst['waiting_time']:.1f} min." if worst else "No vessel schedule is available yet."
    elif "truck" in message:
        text = f"Truck utilization is {m.get('truck_utilization',0):.1f}%. If trucks are reduced, resource contention will increase where vessel operations overlap."
    elif "cost" in message:
        text = f"The demo cost model estimates ₹{m.get('total_cost',0):,.0f} of operational impact using transparent assumed rates. These are simulation assumptions, not real port tariffs."
    elif "yard" in message:
        text = f"Current modeled yard usage is {m.get('yard_utilization',0):.1f}%. If capacity tightens further, redistribute containers to available yard blocks before accepting additional load."
    else:
        text = f"PortMind sees {len(sched)} vessels, {m.get('crane_utilization',0):.1f}% crane utilization, {m.get('truck_utilization',0):.1f}% truck utilization and {m.get('average_waiting',0):.1f} min average waiting. Try asking about delay impact, cranes, trucks, yards or cost."
    return {"answer": text}

@app.post("/api/monte-carlo")
def monte_carlo(req: Scenario):
    base = schedule(req)
    samples = []
    random.seed(42)
    for _ in range(60):
        sim = Scenario(**req.model_dump())
        sim.delay_minutes = max(0, req.delay_minutes + random.gauss(0, 12))
        if random.random() < 0.25:
            sim.failed_crane = req.failed_crane or random.randint(1, max(1, auto_cranes(req.resources.vessels, req.resources.cranes)))
        sim.truck_delta = req.truck_delta + (random.choice([-1, 0, 0, 1]))
        r = schedule(sim)
        samples.append(r["metrics"]["average_waiting"])
    samples.sort()
    p50 = samples[len(samples)//2]
    p90 = samples[int(len(samples)*0.9)]
    high = sum(1 for x in samples if x > 60) / len(samples) * 100
    return {"average_waiting": sum(samples) / len(samples), "p50_waiting": p50, "p90_waiting": p90, "max_waiting": max(samples), "average_queue": round(sum(schedule(Scenario(**req.model_dump()))["metrics"]["queue"] for _ in range(1)), 1), "average_cost": base["metrics"]["total_cost"], "base_average_wait": base["metrics"]["average_waiting"], "samples": samples}

@app.get("/api/presets")
def presets():
    return [{"id": k, "label": v["label"]} for k,v in SCENARIO_PRESETS.items()]
