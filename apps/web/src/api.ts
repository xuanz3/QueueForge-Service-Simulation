import type {
  CreateRunRequest,
  JsonObject,
  ProblemDetail,
  RunRecord,
  SystemStatus,
} from "./domain";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:18086").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly problem?: ProblemDetail,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let problem: ProblemDetail | undefined;
    try {
      problem = (await response.json()) as ProblemDetail;
    } catch {
      problem = undefined;
    }
    const message =
      problem?.detail ??
      problem?.message ??
      problem?.title ??
      `Request failed with HTTP ${response.status}`;
    throw new ApiError(message, response.status, problem);
  }

  return (await response.json()) as T;
}

export const controlPlaneApi = {
  systemStatus(signal?: AbortSignal): Promise<SystemStatus> {
    return request<SystemStatus>("/api/system/status", { signal });
  },

  createRun(payload: CreateRunRequest): Promise<RunRecord> {
    return request<RunRecord>("/api/runs", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getRun(id: string, signal?: AbortSignal): Promise<RunRecord> {
    return request<RunRecord>(`/api/runs/${id}`, { signal });
  },

  getResult(id: string): Promise<JsonObject> {
    return request<JsonObject>(`/api/runs/${id}/result`);
  },

  cancelRun(id: string): Promise<RunRecord> {
    return request<RunRecord>(`/api/runs/${id}/cancel`, { method: "POST" });
  },
};

export function isTerminal(status: RunRecord["status"]): boolean {
  return status === "SUCCEEDED" || status === "FAILED" || status === "CANCELLED";
}
