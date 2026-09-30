export const SCENARIOS = [
  {
    id: "normal",
    name: "Normal Operations",
    description:
      "Baseline port operations.",
    scenario: {
      delayedVessel: "",
      delayMinutes: 0,
      failedCrane: "",
      closedBerth: "",
      weather: "Normal",
      truckShortage: 0,
      blockedYard: "",
      yardReduction: 0,
    },
  },

  {
    id: "vessel-delay",
    name: "Vessel Delay",
    description:
      "Delay one vessel and reschedule operations.",
    scenario: {
      delayedVessel: "V002",
      delayMinutes: 90,
      failedCrane: "",
      closedBerth: "",
      weather: "Normal",
      truckShortage: 0,
      blockedYard: "",
      yardReduction: 0,
    },
  },

  {
    id: "crane-failure",
    name: "Crane Failure",
    description:
      "Remove one crane from operations.",
    scenario: {
      delayedVessel: "",
      delayMinutes: 0,
      failedCrane: 1,
      closedBerth: "",
      weather: "Normal",
      truckShortage: 0,
      blockedYard: "",
      yardReduction: 0,
    },
  },

  {
    id: "storm",
    name: "Storm",
    description:
      "Heavy weather slows port operations.",
    scenario: {
      delayedVessel: "",
      delayMinutes: 0,
      failedCrane: "",
      closedBerth: "",
      weather: "Storm",
      truckShortage: 0,
      blockedYard: "",
      yardReduction: 20,
    },
  },
];