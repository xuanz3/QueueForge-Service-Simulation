package dev.queueforge.controlplane.run;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

@Repository
public class RunRepository {
    private static final RowMapper<RunRecord> ROW_MAPPER = RunRepository::mapRow;
    private final JdbcTemplate jdbc;

    public RunRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void insert(UUID id, RunType type, String requestJson, Instant createdAt) {
        jdbc.update("""
                INSERT INTO queueforge_run (
                    run_id, run_type, status, request_json, created_at
                ) VALUES (?, ?, 'QUEUED', ?, ?)
                """, id, type.name(), requestJson, atUtc(createdAt));
    }

    public Optional<RunRecord> find(UUID id) {
        return jdbc.query("SELECT * FROM queueforge_run WHERE run_id = ?", ROW_MAPPER, id)
                .stream()
                .findFirst();
    }

    public List<RunRecord> findRecent(int limit) {
        return jdbc.query("""
                SELECT * FROM queueforge_run
                ORDER BY created_at DESC
                LIMIT ?
                """, ROW_MAPPER, limit);
    }

    public boolean markRunning(UUID id, Instant startedAt) {
        return jdbc.update("""
                UPDATE queueforge_run
                SET status = 'RUNNING', started_at = ?, version = version + 1
                WHERE run_id = ? AND status = 'QUEUED' AND cancel_requested = FALSE
                """, atUtc(startedAt), id) == 1;
    }

    public void setProcessId(UUID id, long processId) {
        jdbc.update("""
                UPDATE queueforge_run
                SET process_id = ?, version = version + 1
                WHERE run_id = ? AND status = 'RUNNING'
                """, processId, id);
    }

    public boolean requestCancellation(UUID id) {
        return jdbc.update("""
                UPDATE queueforge_run
                SET cancel_requested = TRUE, version = version + 1
                WHERE run_id = ? AND status IN ('QUEUED', 'RUNNING')
                """, id) == 1;
    }

    public boolean isCancellationRequested(UUID id) {
        Boolean value = jdbc.queryForObject(
                "SELECT cancel_requested FROM queueforge_run WHERE run_id = ?",
                Boolean.class,
                id);
        return Boolean.TRUE.equals(value);
    }

    public void markSucceeded(UUID id, String resultJson, Instant completedAt) {
        jdbc.update("""
                UPDATE queueforge_run
                SET status = 'SUCCEEDED', result_json = ?, completed_at = ?,
                    process_id = NULL, version = version + 1
                WHERE run_id = ? AND status = 'RUNNING' AND cancel_requested = FALSE
                """, resultJson, atUtc(completedAt), id);
    }

    public void markFailed(UUID id, String errorCode, String errorMessage, Instant completedAt) {
        jdbc.update("""
                UPDATE queueforge_run
                SET status = 'FAILED', error_code = ?, error_message = ?, completed_at = ?,
                    process_id = NULL, version = version + 1
                WHERE run_id = ? AND status IN ('QUEUED', 'RUNNING')
                """, errorCode, truncate(errorMessage, 4000), atUtc(completedAt), id);
    }

    public void markCancelled(UUID id, Instant completedAt) {
        jdbc.update("""
                UPDATE queueforge_run
                SET status = 'CANCELLED', cancel_requested = TRUE, completed_at = ?,
                    process_id = NULL, version = version + 1
                WHERE run_id = ? AND status IN ('QUEUED', 'RUNNING')
                """, atUtc(completedAt), id);
    }

    public int failIncompleteRuns(Instant completedAt) {
        return jdbc.update("""
                UPDATE queueforge_run
                SET status = 'FAILED', error_code = 'CONTROL_PLANE_RESTARTED',
                    error_message = 'The control plane restarted before the worker completed.',
                    completed_at = ?, process_id = NULL, version = version + 1
                WHERE status IN ('QUEUED', 'RUNNING')
                """, atUtc(completedAt));
    }

    private static RunRecord mapRow(ResultSet rs, int rowNumber) throws SQLException {
        return new RunRecord(
                rs.getObject("run_id", UUID.class),
                RunType.valueOf(rs.getString("run_type")),
                RunStatus.valueOf(rs.getString("status")),
                rs.getString("request_json"),
                rs.getString("result_json"),
                rs.getString("error_code"),
                rs.getString("error_message"),
                nullableLong(rs, "process_id"),
                toInstant(rs, "created_at"),
                toNullableInstant(rs, "started_at"),
                toNullableInstant(rs, "completed_at"),
                rs.getBoolean("cancel_requested"));
    }

    private static Long nullableLong(ResultSet rs, String column) throws SQLException {
        long value = rs.getLong(column);
        return rs.wasNull() ? null : value;
    }

    private static Instant toInstant(ResultSet rs, String column) throws SQLException {
        return rs.getObject(column, OffsetDateTime.class).toInstant();
    }

    private static Instant toNullableInstant(ResultSet rs, String column) throws SQLException {
        OffsetDateTime value = rs.getObject(column, OffsetDateTime.class);
        return value == null ? null : value.toInstant();
    }

    private static OffsetDateTime atUtc(Instant instant) {
        return OffsetDateTime.ofInstant(instant, ZoneOffset.UTC);
    }

    private static String truncate(String message, int maximumLength) {
        if (message == null) {
            return null;
        }
        return message.length() <= maximumLength ? message : message.substring(0, maximumLength);
    }
}
