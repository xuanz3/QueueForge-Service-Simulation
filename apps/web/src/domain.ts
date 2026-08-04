export type RunType = "SIMULATION" | "ANALYTICS";
export type RunStatus = "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED";

export type SystemStatus = {
  service: string;
  version: string;
  status: string;
  database: string;
  workers: Record<string, string>;
  capacity?: {
    maximum: number;
    admitted: number;
    available: number;
  };
  telemetry?: Record<string, number>;
};

export type Scenario = {
  schemaVersion: "1.0";
  simulation: {
    durationMinutes: number;
    seed: number;
  };
  arrivals: {
    type: "poisson";
    ratePerHour: number;
  };
  service: {
    type: "triangular";
    minimumMinutes: number;
    modeMinutes: number;
    maximumMinutes: number;
  };
  queue: {
    discipline: "fifo" | "priority_fifo";
    serverCount: number;
    priorityCustomerRatio: number;
  };
};

export type AnalyticsSettings = {
  serverCounts: number[];
  runs: number;
  seedStart: number;
  targetP95Wait: number;
  targetMaxQueue: number;
  targetMaxUtilisation: number;
  requiredSuccessRate: number;
};

export type CreateRunRequest = {
  type: RunType;
  scenario: Scenario;
  serverCounts?: number[];
  runs?: number;
  seedStart?: number;
  targetP95Wait?: number;
  targetMaxQueue?: number;
  targetMaxUtilisation?: number;
  requiredSuccessRate?: number;
};

export type RunRecord = {
  id: string;
  type: RunType;
  status: RunStatus;
  processId: number | null;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
  cancelRequested: boolean;
  errorCode: string | null;
  errorMessage: string | null;
  links: Record<string, string>;
};

export type ProblemDetail = {
  status?: number;
  title?: string;
  detail?: string;
  message?: string;
};

export type JsonObject = Record<string, unknown>;
