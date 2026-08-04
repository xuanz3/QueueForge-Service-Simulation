import type { AnalyticsSettings, Scenario } from "./domain";

export type ScenarioPreset = {
  id: string;
  name: string;
  description: string;
  scenario: Scenario;
};

export const baseScenario: Scenario = {
  schemaVersion: "1.0",
  simulation: { durationMinutes: 480, seed: 20260801 },
  arrivals: { type: "poisson", ratePerHour: 24 },
  service: {
    type: "triangular",
    minimumMinutes: 3,
    modeMinutes: 6,
    maximumMinutes: 12,
  },
  queue: {
    discipline: "priority_fifo",
    serverCount: 4,
    priorityCustomerRatio: 0.15,
  },
};

export const defaultAnalytics: AnalyticsSettings = {
  serverCounts: [3, 4, 5],
  runs: 40,
  seedStart: 20260801,
  targetP95Wait: 10,
  targetMaxQueue: 20,
  targetMaxUtilisation: 0.85,
  requiredSuccessRate: 0.9,
};

export const presets: ScenarioPreset[] = [
  {
    id: "balanced",
    name: "Balanced day",
    description: "The committed eight-hour reference scenario.",
    scenario: baseScenario,
  },
  {
    id: "morning-peak",
    name: "Morning peak",
    description: "Higher arrival pressure with the same service distribution.",
    scenario: {
      ...baseScenario,
      arrivals: { ...baseScenario.arrivals, ratePerHour: 34 },
      queue: { ...baseScenario.queue, serverCount: 5 },
    },
  },
  {
    id: "lean-team",
    name: "Lean team",
    description: "A deliberately constrained team for queue-risk exploration.",
    scenario: {
      ...baseScenario,
      arrivals: { ...baseScenario.arrivals, ratePerHour: 28 },
      queue: { ...baseScenario.queue, serverCount: 3 },
    },
  },
];

export function cloneScenario(scenario: Scenario): Scenario {
  return JSON.parse(JSON.stringify(scenario)) as Scenario;
}

export function validateScenario(scenario: Scenario): string[] {
  const errors: string[] = [];
  if (scenario.simulation.durationMinutes <= 0 || scenario.simulation.durationMinutes > 1440) {
    errors.push("Duration must be between 1 and 1,440 minutes.");
  }
  if (scenario.simulation.seed < 0) errors.push("Seed must be non-negative.");
  if (scenario.arrivals.ratePerHour <= 0 || scenario.arrivals.ratePerHour > 600) {
    errors.push("Arrival rate must be between 0 and 600 per hour.");
  }
  const { minimumMinutes, modeMinutes, maximumMinutes } = scenario.service;
  if (!(minimumMinutes > 0 && minimumMinutes <= modeMinutes && modeMinutes <= maximumMinutes && maximumMinutes <= 240)) {
    errors.push("Service times must satisfy 0 < minimum ≤ mode ≤ maximum ≤ 240.");
  }
  if (scenario.queue.serverCount < 1 || scenario.queue.serverCount > 100) {
    errors.push("Server count must be between 1 and 100.");
  }
  if (scenario.queue.priorityCustomerRatio < 0 || scenario.queue.priorityCustomerRatio > 1) {
    errors.push("Priority ratio must be between 0 and 1.");
  }
  return errors;
}

export function validateAnalytics(settings: AnalyticsSettings): string[] {
  const errors: string[] = [];
  if (settings.serverCounts.length < 1 || settings.serverCounts.length > 10) {
    errors.push("Compare between 1 and 10 staffing values.");
  }
  if (new Set(settings.serverCounts).size !== settings.serverCounts.length) {
    errors.push("Staffing values must not contain duplicates.");
  }
  if (settings.serverCounts.some((value) => value < 1 || value > 100)) {
    errors.push("Each staffing value must be between 1 and 100.");
  }
  if (settings.runs < 2 || settings.runs > 200) {
    errors.push("Runs per option must be between 2 and 200.");
  }
  if (settings.targetMaxUtilisation <= 0 || settings.targetMaxUtilisation > 1) {
    errors.push("Maximum utilisation must be between 0 and 1.");
  }
  if (settings.requiredSuccessRate <= 0 || settings.requiredSuccessRate > 1) {
    errors.push("Required success rate must be between 0 and 1.");
  }
  return errors;
}
