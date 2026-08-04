import { useEffect, useMemo, useRef, useState } from "react";
import { ApiError, controlPlaneApi, isTerminal } from "./api";
import type {
  AnalyticsSettings,
  CreateRunRequest,
  JsonObject,
  RunRecord,
  RunType,
  Scenario,
  SystemStatus,
} from "./domain";
import {
  baseScenario,
  cloneScenario,
  defaultAnalytics,
  presets,
  validateAnalytics,
  validateScenario,
} from "./scenario";

type ConnectionState =
  | { kind: "loading" }
  | { kind: "ready"; data: SystemStatus }
  | { kind: "error"; message: string };

type ActiveRun = {
  record: RunRecord;
  result: JsonObject | null;
};

const number = (value: unknown, fallback = 0): number =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

const object = (value: unknown): JsonObject =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonObject)
    : {};

const nested = (source: unknown, ...path: string[]): unknown => {
  let current: unknown = source;
  for (const key of path) current = object(current)[key];
  return current;
};

const formatNumber = (value: unknown, digits = 1): string =>
  number(value).toLocaleString(undefined, { maximumFractionDigits: digits });

const formatPercent = (value: unknown): string =>
  `${(number(value) * 100).toFixed(1)}%`;

function Field({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <div className="input-shell">
        <input
          type="number"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(event) => onChange(Number(event.target.value))}
        />
        {suffix && <small>{suffix}</small>}
      </div>
    </label>
  );
}

function Metric({
  label,
  value,
  note,
}: {
  label: string;
  value: string;
  note?: string;
}) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {note && <small>{note}</small>}
    </article>
  );
}

function SimulationResult({ result }: { result: JsonObject }) {
  const metrics = object(result.metrics);
  const counts = object(metrics.counts);
  const waiting = object(metrics.waitingMinutes);
  const queue = object(metrics.queueLength);
  const utilisation = result.utilisation ?? metrics.utilisation;
  const throughput = metrics.throughputPerHour ?? result.throughputPerHour;

  return (
    <section className="result-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">SIMULATION EVIDENCE</p>
          <h2>Queue outcome</h2>
        </div>
        <span className="pill success">Deterministic result</span>
      </div>
      <div className="metrics-grid">
        <Metric label="Customers completed" value={formatNumber(counts.completed ?? result.completedCustomers, 0)} />
        <Metric label="P95 wait" value={`${formatNumber(waiting.p95 ?? metrics.p95WaitMinutes)} min`} />
        <Metric label="Maximum queue" value={formatNumber(queue.maximum ?? metrics.maximumQueueLength, 0)} />
        <Metric label="Throughput" value={`${formatNumber(throughput)} / hr`} />
        <Metric label="Utilisation" value={formatPercent(utilisation)} />
        <Metric label="Average wait" value={`${formatNumber(waiting.average ?? metrics.averageWaitMinutes)} min`} />
      </div>
      <details className="raw-result">
        <summary>Inspect versioned JSON result</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </section>
  );
}

function AnalyticsResult({ result }: { result: JsonObject }) {
  const variants = Array.isArray(result.variants) ? result.variants.map(object) : [];
  const recommendation = object(result.recommendation);
  const selected = recommendation.serverCount ?? recommendation.selectedServerCount;

  return (
    <section className="result-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">MULTI-SEED ANALYSIS</p>
          <h2>Staffing comparison</h2>
        </div>
        <span className="pill success">
          {selected ? `${formatNumber(selected, 0)} servers selected` : "Analysis complete"}
        </span>
      </div>
      <div className="variant-list">
        {variants.map((variant, index) => {
          const servers = variant.serverCount ?? variant.servers ?? index + 1;
          const successRate = number(
            variant.targetSuccessRate ?? variant.successRate ?? variant.observedSuccessRate,
          );
          const p95 =
            nested(variant, "metrics", "p95WaitMinutes", "mean") ??
            nested(variant, "p95WaitMinutes", "mean") ??
            variant.meanP95WaitMinutes;
          const utilisation =
            nested(variant, "metrics", "utilisation", "mean") ??
            nested(variant, "utilisation", "mean") ??
            variant.meanUtilisation;
          return (
            <article className="variant" key={`${servers}-${index}`}>
              <div className="variant-title">
                <strong>{formatNumber(servers, 0)} servers</strong>
                <span>{formatPercent(successRate)} target success</span>
              </div>
              <div className="bar" aria-label={`${formatPercent(successRate)} target success`}>
                <i style={{ width: `${Math.min(100, successRate * 100)}%` }} />
              </div>
              <div className="variant-details">
                <span>P95 wait <b>{formatNumber(p95)} min</b></span>
                <span>Utilisation <b>{formatPercent(utilisation)}</b></span>
              </div>
            </article>
          );
        })}
      </div>
      {variants.length === 0 && (
        <p className="empty">The report completed, but no variant summary was recognised. Inspect the JSON evidence below.</p>
      )}
      <details className="raw-result">
        <summary>Inspect versioned analytics report</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </section>
  );
}

export default function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "loading" });
  const [mode, setMode] = useState<RunType>("ANALYTICS");
  const [scenario, setScenario] = useState<Scenario>(() => cloneScenario(baseScenario));
  const [analytics, setAnalytics] = useState<AnalyticsSettings>({ ...defaultAnalytics });
  const [run, setRun] = useState<ActiveRun | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const pollAbort = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    controlPlaneApi
      .systemStatus(controller.signal)
      .then((data) => setConnection({ kind: "ready", data }))
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setConnection({
            kind: "error",
            message: error instanceof Error ? error.message : "Unable to reach the local control plane.",
          });
        }
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!run || isTerminal(run.record.status)) return;
    const controller = new AbortController();
    pollAbort.current = controller;
    const timer = window.setInterval(async () => {
      try {
        const record = await controlPlaneApi.getRun(run.record.id, controller.signal);
        if (isTerminal(record.status)) {
          window.clearInterval(timer);
          const result =
            record.status === "SUCCEEDED"
              ? await controlPlaneApi.getResult(record.id)
              : null;
          setRun({ record, result });
        } else {
          setRun((current) => (current ? { ...current, record } : current));
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          setSubmitError(error instanceof Error ? error.message : "Run status could not be refreshed.");
        }
      }
    }, 1000);
    return () => {
      controller.abort();
      window.clearInterval(timer);
    };
  }, [run?.record.id, run?.record.status]);

  const validationErrors = useMemo(
    () => [
      ...validateScenario(scenario),
      ...(mode === "ANALYTICS" ? validateAnalytics(analytics) : []),
    ],
    [analytics, mode, scenario],
  );

  const updateSimulation = (
    values: Partial<Scenario["simulation"]>,
  ) => {
    setScenario((current) => ({
      ...current,
      simulation: { ...current.simulation, ...values },
    }));
  };

  const updateArrivals = (
    values: Partial<Scenario["arrivals"]>,
  ) => {
    setScenario((current) => ({
      ...current,
      arrivals: { ...current.arrivals, ...values },
    }));
  };

  const updateService = (
    values: Partial<Scenario["service"]>,
  ) => {
    setScenario((current) => ({
      ...current,
      service: { ...current.service, ...values },
    }));
  };

  const updateQueue = (
    values: Partial<Scenario["queue"]>,
  ) => {
    setScenario((current) => ({
      ...current,
      queue: { ...current.queue, ...values },
    }));
  };

  const submit = async () => {
    if (validationErrors.length > 0 || connection.kind !== "ready") return;
    setSubmitError(null);
    pollAbort.current?.abort();
    try {
      const payload: CreateRunRequest = {
        type: mode,
        scenario,
        ...(mode === "ANALYTICS" ? analytics : {}),
      };
      const record = await controlPlaneApi.createRun(payload);
      setRun({ record, result: null });
    } catch (error) {
      setSubmitError(
        error instanceof ApiError || error instanceof Error
          ? error.message
          : "The run could not be submitted.",
      );
    }
  };

  const cancel = async () => {
    if (!run || isTerminal(run.record.status)) return;
    try {
      const record = await controlPlaneApi.cancelRun(run.record.id);
      setRun((current) => (current ? { ...current, record } : current));
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Cancellation failed.");
    }
  };

  const busy = run ? !isTerminal(run.record.status) : false;
  const connectionReady = connection.kind === "ready";

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="QueueForge home">
          <span className="brand-mark">QF</span>
          <span>
            <strong>QueueForge</strong>
            <small>Operations studio</small>
          </span>
        </a>
        <div className={`connection ${connection.kind}`}>
          <i />
          <span>
            {connection.kind === "ready"
              ? `API ${connection.data.version} · ${connection.data.database}${
                  connection.data.capacity
                    ? ` · ${connection.data.capacity.available}/${connection.data.capacity.maximum} slots`
                    : ""
                }`
              : connection.kind === "loading"
                ? "Checking local stack"
                : connection.message}
          </span>
        </div>
      </header>

      <main id="top">
        <section className="hero">
          <div>
            <p className="eyebrow">SERVICE OPERATIONS SIMULATION</p>
            <h1>Test staffing decisions before they affect a real queue.</h1>
            <p className="hero-copy">
              Configure a reproducible service scenario, run the deterministic engine,
              and compare staffing options with multi-seed evidence.
            </p>
          </div>
          <aside className="hero-stat">
            <span>Current workflow</span>
            <strong>{mode === "ANALYTICS" ? "Staffing comparison" : "Single simulation"}</strong>
            <small>Local-first · no operational data required</small>
          </aside>
        </section>

        <section className="workspace">
          <div className="configuration">
            <div className="mode-switch" role="tablist" aria-label="Run type">
              {(["SIMULATION", "ANALYTICS"] as RunType[]).map((value) => (
                <button
                  key={value}
                  role="tab"
                  aria-selected={mode === value}
                  className={mode === value ? "active" : ""}
                  onClick={() => setMode(value)}
                  disabled={busy}
                >
                  {value === "SIMULATION" ? "Single simulation" : "Staffing analysis"}
                </button>
              ))}
            </div>

            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">01 · STARTING POINT</p>
                  <h2>Scenario preset</h2>
                </div>
                <button className="text-button" onClick={() => setScenario(cloneScenario(baseScenario))} disabled={busy}>
                  Reset
                </button>
              </div>
              <div className="preset-grid">
                {presets.map((preset) => (
                  <button
                    className="preset"
                    key={preset.id}
                    onClick={() => setScenario(cloneScenario(preset.scenario))}
                    disabled={busy}
                  >
                    <strong>{preset.name}</strong>
                    <span>{preset.description}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">02 · DEMAND AND SERVICE</p>
                  <h2>Operating assumptions</h2>
                </div>
              </div>
              <div className="form-grid">
                <Field label="Operating window" value={scenario.simulation.durationMinutes} min={1} max={1440} suffix="minutes" onChange={(value) => updateSimulation({ durationMinutes: value })} />
                <Field label="Arrival rate" value={scenario.arrivals.ratePerHour} min={0.1} max={600} step={0.5} suffix="per hour" onChange={(value) => updateArrivals({ ratePerHour: value })} />
                <Field label="Minimum service" value={scenario.service.minimumMinutes} min={0.1} max={240} step={0.5} suffix="minutes" onChange={(value) => updateService({ minimumMinutes: value })} />
                <Field label="Typical service" value={scenario.service.modeMinutes} min={0.1} max={240} step={0.5} suffix="minutes" onChange={(value) => updateService({ modeMinutes: value })} />
                <Field label="Maximum service" value={scenario.service.maximumMinutes} min={0.1} max={240} step={0.5} suffix="minutes" onChange={(value) => updateService({ maximumMinutes: value })} />
                <Field label="Deterministic seed" value={scenario.simulation.seed} min={0} max={999999999} onChange={(value) => updateSimulation({ seed: value })} />
              </div>
            </section>

            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">03 · QUEUE POLICY</p>
                  <h2>Staffing and priority</h2>
                </div>
              </div>
              <div className="form-grid">
                <Field label="Active servers" value={scenario.queue.serverCount} min={1} max={100} onChange={(value) => updateQueue({ serverCount: value })} />
                <Field label="Priority customers" value={scenario.queue.priorityCustomerRatio * 100} min={0} max={100} step={1} suffix="percent" onChange={(value) => updateQueue({ priorityCustomerRatio: value / 100 })} />
                <label className="field field-wide">
                  <span>Queue discipline</span>
                  <select value={scenario.queue.discipline} onChange={(event) => updateQueue({ discipline: event.target.value as Scenario["queue"]["discipline"] })}>
                    <option value="priority_fifo">Priority FIFO</option>
                    <option value="fifo">FIFO</option>
                  </select>
                </label>
              </div>
            </section>

            {mode === "ANALYTICS" && (
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">04 · DECISION POLICY</p>
                    <h2>Comparison settings</h2>
                  </div>
                </div>
                <div className="form-grid">
                  <label className="field field-wide">
                    <span>Server counts</span>
                    <input
                      value={analytics.serverCounts.join(", ")}
                      onChange={(event) =>
                        setAnalytics((current) => ({
                          ...current,
                          serverCounts: event.target.value
                            .split(",")
                            .map((value) => Number(value.trim()))
                            .filter((value) => Number.isFinite(value)),
                        }))
                      }
                    />
                  </label>
                  <Field label="Runs per option" value={analytics.runs} min={2} max={200} onChange={(runs) => setAnalytics((current) => ({ ...current, runs }))} />
                  <Field label="Target P95 wait" value={analytics.targetP95Wait} min={0.1} max={240} step={0.5} suffix="minutes" onChange={(targetP95Wait) => setAnalytics((current) => ({ ...current, targetP95Wait }))} />
                  <Field label="Maximum queue" value={analytics.targetMaxQueue} min={0} max={100000} onChange={(targetMaxQueue) => setAnalytics((current) => ({ ...current, targetMaxQueue }))} />
                  <Field label="Maximum utilisation" value={analytics.targetMaxUtilisation * 100} min={1} max={100} suffix="percent" onChange={(value) => setAnalytics((current) => ({ ...current, targetMaxUtilisation: value / 100 }))} />
                  <Field label="Required success" value={analytics.requiredSuccessRate * 100} min={1} max={100} suffix="percent" onChange={(value) => setAnalytics((current) => ({ ...current, requiredSuccessRate: value / 100 }))} />
                </div>
              </section>
            )}

            {validationErrors.length > 0 && (
              <div className="validation" role="alert">
                <strong>Review the scenario</strong>
                <ul>{validationErrors.map((error) => <li key={error}>{error}</li>)}</ul>
              </div>
            )}

            {submitError && <div className="validation error" role="alert">{submitError}</div>}

            <div className="action-row">
              <button
                className="primary"
                onClick={submit}
                disabled={!connectionReady || busy || validationErrors.length > 0}
              >
                {busy ? "Run in progress" : mode === "ANALYTICS" ? "Compare staffing options" : "Run simulation"}
              </button>
              <span>{connectionReady ? "Uses the local Java control plane" : "Waiting for the local API"}</span>
            </div>
          </div>

          <aside className="run-sidebar">
            <div className="sidebar-sticky">
              <p className="eyebrow">LIVE RUN</p>
              {!run && (
                <div className="empty-card">
                  <strong>No run submitted</strong>
                  <p>Configure a scenario and start a simulation or staffing comparison.</p>
                </div>
              )}
              {run && (
                <div className="run-card">
                  <div className="run-status">
                    <span className={`status-dot ${run.record.status.toLowerCase()}`} />
                    <div>
                      <strong>{run.record.status}</strong>
                      <small>{run.record.type}</small>
                    </div>
                  </div>
                  <dl>
                    <div><dt>Run ID</dt><dd>{run.record.id.slice(0, 8)}</dd></div>
                    <div><dt>Created</dt><dd>{new Date(run.record.createdAt).toLocaleTimeString()}</dd></div>
                    <div><dt>Process</dt><dd>{run.record.processId ?? "Pending"}</dd></div>
                  </dl>
                  {busy && (
                    <>
                      <div className="progress"><i /></div>
                      <button className="danger" onClick={cancel}>Cancel run</button>
                    </>
                  )}
                  {run.record.errorMessage && <p className="run-error">{run.record.errorMessage}</p>}
                </div>
              )}
              <div className="stack-card">
                <span>Execution path</span>
                <ol>
                  <li><b>React</b><small>Validates and submits</small></li>
                  <li><b>Java</b><small>Persists and supervises</small></li>
                  <li><b>{mode === "ANALYTICS" ? "Python + C++" : "C++"}</b><small>Produces evidence</small></li>
                  <li><b>PostgreSQL</b><small>Retains lifecycle state</small></li>
                </ol>
              </div>
            </div>
          </aside>
        </section>

        {run?.result && (
          run.record.type === "SIMULATION"
            ? <SimulationResult result={run.result} />
            : <AnalyticsResult result={run.result} />
        )}
      </main>

      <footer>
        <span>QueueForge portfolio project</span>
        <span>Fictional scenario · not operational staffing advice</span>
      </footer>
    </div>
  );
}
