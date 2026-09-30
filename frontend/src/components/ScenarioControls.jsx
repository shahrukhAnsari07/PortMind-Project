import {
  SCENARIOS,
} from "../data/scenarios";

import {
  useSimulationContext,
} from "../context/SimulationContext";


function ScenarioControls() {
  const {
    scenario,
    setScenario,
    vessels,
    run,
    loading,
  } = useSimulationContext();

  const update = (
    field,
    value
  ) => {
    setScenario(current => ({
      ...current,
      [field]: value,
    }));
  };

  const applyPreset = (
    preset
  ) => {
    setScenario({
      ...preset.scenario,
    });
  };

  return (
    <div className="panel">

      <div className="panel-header">

        <div>
          <h3>
            Disruption Scenario
          </h3>

          <p>
            Inject an operational
            disruption and rerun the
            digital twin.
          </p>
        </div>

        <button
          className="primary-btn"
          onClick={run}
          disabled={loading}
        >
          {loading
            ? "Simulating..."
            : "Apply Scenario"}
        </button>

      </div>


      <div className="preset-grid">

        {SCENARIOS.map(
          preset => (
            <button
              key={preset.id}
              className="preset"
              onClick={() =>
                applyPreset(
                  preset
                )
              }
            >
              <strong>
                {preset.name}
              </strong>

              <span>
                {preset.description}
              </span>
            </button>
          )
        )}

      </div>


      <div className="form-grid">

        <label>
          Delayed Vessel

          <select
            value={
              scenario.delayedVessel
            }
            onChange={event =>
              update(
                "delayedVessel",
                event.target.value
              )
            }
          >
            <option value="">
              None
            </option>

            {vessels.map(
              vessel => (
                <option
                  key={vessel.id}
                  value={vessel.id}
                >
                  {vessel.name}
                </option>
              )
            )}
          </select>
        </label>


        <label>
          Delay Duration

          <input
            type="number"
            min="0"
            value={
              scenario.delayMinutes
            }
            onChange={event =>
              update(
                "delayMinutes",
                event.target.value
              )
            }
          />
        </label>


        <label>
          Failed Crane

          <input
            type="number"
            min="1"
            placeholder="None"
            value={
              scenario.failedCrane
            }
            onChange={event =>
              update(
                "failedCrane",
                event.target.value
              )
            }
          />
        </label>


        <label>
          Closed Berth

          <input
            type="number"
            min="1"
            placeholder="None"
            value={
              scenario.closedBerth
            }
            onChange={event =>
              update(
                "closedBerth",
                event.target.value
              )
            }
          />
        </label>


        <label>
          Weather

          <select
            value={scenario.weather}
            onChange={event =>
              update(
                "weather",
                event.target.value
              )
            }
          >
            <option>
              Normal
            </option>

            <option>
              Light Rain
            </option>

            <option>
              Heavy Rain
            </option>

            <option>
              Storm
            </option>

            <option>
              Major Disruption
            </option>
          </select>
        </label>


        <label>
          Truck Shortage

          <input
            type="number"
            min="0"
            value={
              scenario.truckShortage
            }
            onChange={event =>
              update(
                "truckShortage",
                event.target.value
              )
            }
          />
        </label>


        <label>
          Blocked Yard

          <input
            type="number"
            min="1"
            placeholder="None"
            value={
              scenario.blockedYard
            }
            onChange={event =>
              update(
                "blockedYard",
                event.target.value
              )
            }
          />
        </label>


        <label>
          Yard Capacity Reduction %

          <input
            type="number"
            min="0"
            max="100"
            value={
              scenario.yardReduction
            }
            onChange={event =>
              update(
                "yardReduction",
                event.target.value
              )
            }
          />
        </label>

      </div>

    </div>
  );
}

export default ScenarioControls;