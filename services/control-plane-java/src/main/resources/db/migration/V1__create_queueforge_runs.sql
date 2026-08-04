CREATE TABLE queueforge_run (
    run_id UUID PRIMARY KEY,
    run_type VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    request_json TEXT NOT NULL,
    result_json TEXT,
    error_code VARCHAR(80),
    error_message TEXT,
    process_id BIGINT,
    cancel_requested BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT queueforge_run_type_check
        CHECK (run_type IN ('SIMULATION', 'ANALYTICS')),
    CONSTRAINT queueforge_run_status_check
        CHECK (status IN ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED')),
    CONSTRAINT queueforge_run_terminal_time_check
        CHECK (
            (status IN ('SUCCEEDED', 'FAILED', 'CANCELLED') AND completed_at IS NOT NULL)
            OR status IN ('QUEUED', 'RUNNING')
        )
);

CREATE INDEX queueforge_run_created_at_idx
    ON queueforge_run (created_at DESC);

CREATE INDEX queueforge_run_status_idx
    ON queueforge_run (status, created_at DESC);
