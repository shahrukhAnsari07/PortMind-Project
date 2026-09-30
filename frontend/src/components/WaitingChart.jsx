function WaitingChart({
  data,
}) {
  const schedule =
    data?.schedule || [];

  const maxWaiting =
    Math.max(
      1,
      ...schedule.map(
        row =>
          Number(row.waiting) || 0
      )
    );


  return (
    <div className="panel">

      <div className="panel-header">
        <div>
          <h3>
            Vessel Waiting Time
          </h3>

          <p>
            Waiting time by vessel.
          </p>
        </div>
      </div>


      {!schedule.length ? (
        <div className="empty-state">
          No waiting-time data.
        </div>
      ) : (

        <div className="bar-chart">

          {schedule.map(
            row => {

              const value =
                Number(
                  row.waiting
                ) || 0;

              const height =
                (value / maxWaiting)
                * 100;

              return (
                <div
                  className="chart-column"
                  key={
                    row.vessel_id
                  }
                >

                  <div className="chart-value">
                    {value}m
                  </div>

                  <div className="chart-bar-container">

                    <div
                      className="chart-bar"
                      style={{
                        height:
                          `${Math.max(
                            4,
                            height
                          )}%`,
                      }}
                    />

                  </div>

                  <span>
                    {row.vessel}
                  </span>

                </div>
              );
            }
          )}

        </div>
      )}

    </div>
  );
}

export default WaitingChart;