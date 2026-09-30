function Comparison({
  data,
}) {
  const comparison =
    data?.comparison;

  if (!comparison) {
    return (
      <div className="panel">

        <div className="empty-state">
          Run a simulation with a
          scenario to see before/after
          comparison.
        </div>

      </div>
    );
  }


  const waitingChange =
    comparison.waiting_reduction;

  return (
    <div className="panel">

      <div className="panel-header">

        <div>
          <h3>
            Before / After Comparison
          </h3>

          <p>
            Baseline versus current
            disruption scenario.
          </p>
        </div>

      </div>


      <div className="comparison-grid">

        <div className="comparison-card">
          <span>
            Baseline Waiting
          </span>

          <strong>
            {
              comparison
                .average_waiting_before
            }
            {" min"}
          </strong>
        </div>


        <div className="comparison-card">
          <span>
            Scenario Waiting
          </span>

          <strong>
            {
              comparison
                .average_waiting_after
            }
            {" min"}
          </strong>
        </div>


        <div className="comparison-card">
          <span>
            Waiting Difference
          </span>

          <strong>
            {waitingChange > 0
              ? "+"
              : ""}
            {waitingChange}
            {" min"}
          </strong>
        </div>


        <div className="comparison-card">
          <span>
            Queue
          </span>

          <strong>
            {
              comparison
                .queue_before
            }
            {" → "}
            {
              comparison
                .queue_after
            }
          </strong>
        </div>

      </div>

    </div>
  );
}

export default Comparison;