import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  simulate,
  health,
} from "../services/api";

import {
  DEFAULT_RESOURCES,
  DEFAULT_SCENARIO,
  DEFAULT_VESSELS,
} from "../utils/constants";


function buildPayload(
  resources,
  vessels,
  scenario
) {
  return {
    resources: {
      vessels:
        Number(resources.vessels),

      berths:
        Number(resources.berths),

      cranes:
        resources.cranes === ""
          ? null
          : Number(resources.cranes),

      trucks:
        Number(resources.trucks),

      yards:
        Number(resources.yards),
    },

    vessels,

    scenario: {
      delayed_vessel:
        scenario.delayedVessel || null,

      delay_minutes:
        Number(
          scenario.delayMinutes || 0
        ),

      failed_crane:
        scenario.failedCrane
          ? Number(
              scenario.failedCrane
            )
          : null,

      closed_berth:
        scenario.closedBerth
          ? Number(
              scenario.closedBerth
            )
          : null,

      weather:
        scenario.weather,

      truck_shortage:
        Number(
          scenario.truckShortage || 0
        ),

      blocked_yard:
        scenario.blockedYard
          ? Number(
              scenario.blockedYard
            )
          : null,

      yard_reduction_pct:
        Number(
          scenario.yardReduction || 0
        ),
    },

    objective:
      "min_waiting",
  };
}


export function useSimulation() {
  const [
    resources,
    setResources,
  ] = useState(
    DEFAULT_RESOURCES
  );

  const [
    vessels,
    setVessels,
  ] = useState(
    DEFAULT_VESSELS
  );

  const [
    scenario,
    setScenario,
  ] = useState(
    DEFAULT_SCENARIO
  );

  const [
    data,
    setData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    apiHealth,
    setApiHealth,
  ] = useState(null);

  const [
    clock,
    setClock,
  ] = useState(0);

  const [
    playback,
    setPlayback,
  ] = useState("stopped");

  const [
    speed,
    setSpeed,
  ] = useState(1);


  const payload = useMemo(
    () =>
      buildPayload(
        resources,
        vessels,
        scenario
      ),
    [
      resources,
      vessels,
      scenario,
    ]
  );


  const run = useCallback(
    async () => {
      setLoading(true);
      setError("");

      try {
        const result =
          await simulate(
            payload
          );

        setData(result);
        setClock(0);
        setPlayback(
          "stopped"
        );
      } catch (err) {
        setError(
          err.message ||
          "Simulation failed."
        );
      } finally {
        setLoading(false);
      }
    },
    [payload]
  );


  const checkHealth =
    useCallback(
      async () => {
        try {
          const result =
            await health();

          setApiHealth(result);
        } catch {
          setApiHealth({
            status: "offline",
          });
        }
      },
      []
    );


  useEffect(() => {
    checkHealth();
  }, [checkHealth]);


  useEffect(() => {
    if (playback !== "running") {
      return undefined;
    }

    const timer =
      window.setInterval(() => {
        setClock(current => {
          const horizon =
            data?.metrics?.horizon ||
            240;

          const next =
            current + speed;

          if (next >= horizon) {
            setPlayback(
              "stopped"
            );

            return horizon;
          }

          return next;
        });
      }, 500);

    return () =>
      window.clearInterval(
        timer
      );
  }, [
    playback,
    speed,
    data,
  ]);


  const start = () => {
    if (!data) {
      run();
      return;
    }

    setClock(0);
    setPlayback("running");
  };


  const pause = () => {
    if (
      playback === "running"
    ) {
      setPlayback("paused");
    }
  };


  const resume = () => {
    if (
      playback === "paused"
    ) {
      setPlayback("running");
    }
  };


  const reset = () => {
    setClock(0);
    setPlayback("stopped");
  };


  const resetProject = () => {
    setResources(
      DEFAULT_RESOURCES
    );

    setVessels(
      DEFAULT_VESSELS
    );

    setScenario(
      DEFAULT_SCENARIO
    );

    setClock(0);
    setPlayback("stopped");
  };


  return {
    resources,
    setResources,

    vessels,
    setVessels,

    scenario,
    setScenario,

    data,
    setData,

    payload,

    loading,
    error,

    apiHealth,

    clock,
    playback,
    speed,
    setSpeed,

    run,
    start,
    pause,
    resume,
    reset,
    resetProject,
  };
}