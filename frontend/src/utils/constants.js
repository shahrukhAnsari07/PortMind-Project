export const NAV_ITEMS = [
  {
    id: "overview",
    label: "Overview",
    icon: "⌂",
  },
  {
    id: "twin",
    label: "Port Digital Twin",
    icon: "⚓",
  },
  {
    id: "inputs",
    label: "Simulation Inputs",
    icon: "⚙",
  },
  {
    id: "vessels",
    label: "Vessels",
    icon: "🚢",
  },
  {
    id: "scheduling",
    label: "Scheduling Engine",
    icon: "📅",
  },
  {
    id: "disruption",
    label: "Disruption Simulator",
    icon: "⚠",
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: "📊",
  },
  {
    id: "report",
    label: "Simulation Report",
    icon: "📄",
  },
];


export const DEFAULT_RESOURCES = {
  vessels: 4,
  berths: 2,
  cranes: 3,
  trucks: 12,
  yards: 4,
};


export const DEFAULT_VESSELS = [
  {
    id: "V001",
    name: "MV Horizon",
    eta: 0,
    containers: 220,
    priority: 3,
  },
  {
    id: "V002",
    name: "Ocean Star",
    eta: 30,
    containers: 180,
    priority: 2,
  },
  {
    id: "V003",
    name: "Pacific Trader",
    eta: 70,
    containers: 260,
    priority: 4,
  },
  {
    id: "V004",
    name: "Atlas Carrier",
    eta: 100,
    containers: 150,
    priority: 1,
  },
];


export const DEFAULT_SCENARIO = {
  delayedVessel: "",
  delayMinutes: 0,
  failedCrane: "",
  closedBerth: "",
  weather: "Normal",
  truckShortage: 0,
  blockedYard: "",
  yardReduction: 0,
};