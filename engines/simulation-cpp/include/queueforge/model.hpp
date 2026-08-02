#pragma once

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace queueforge {

enum class QueueDiscipline {
    Fifo,
    PriorityFifo,
};

enum class EventType {
    Arrival,
    ServiceStart,
    ServiceComplete,
};

struct ServiceDistribution {
    double minimum_minutes = 0.0;
    double mode_minutes = 0.0;
    double maximum_minutes = 0.0;
};

struct SimulationConfig {
    double duration_minutes = 0.0;
    std::uint64_t seed = 0;
    double arrival_rate_per_hour = 0.0;
    ServiceDistribution service;
    QueueDiscipline discipline = QueueDiscipline::Fifo;
    std::size_t server_count = 0;
    double priority_customer_ratio = 0.0;
};

struct Customer {
    std::uint64_t id = 0;
    bool priority = false;
    double arrival_time = 0.0;
    std::optional<double> service_start_time;
    std::optional<double> service_complete_time;
};

struct ServerSnapshot {
    std::size_t id = 0;
    double busy_minutes = 0.0;
    double utilisation = 0.0;
};

struct EventRecord {
    EventType type = EventType::Arrival;
    double time_minutes = 0.0;
    std::uint64_t customer_id = 0;
    std::optional<std::size_t> server_id;
    bool priority = false;
    std::size_t queue_length_after = 0;
};

struct SimulationMetrics {
    std::size_t arrived = 0;
    std::size_t completed = 0;
    std::size_t waiting_at_end = 0;
    std::size_t in_service_at_end = 0;
    double average_wait_minutes = 0.0;
    double median_wait_minutes = 0.0;
    double p95_wait_minutes = 0.0;
    double maximum_wait_minutes = 0.0;
    double average_queue_length = 0.0;
    std::size_t maximum_queue_length = 0;
    double throughput_per_hour = 0.0;
    double overall_utilisation = 0.0;
};

struct SimulationInvariants {
    bool accounting_balanced = false;
    bool utilisation_within_range = false;
    bool chronology_valid = false;
};

struct SimulationResult {
    std::string schema_version = "1.0";
    std::string engine_version = "0.2.0";
    std::uint64_t seed = 0;
    double duration_minutes = 0.0;
    QueueDiscipline discipline = QueueDiscipline::Fifo;
    SimulationMetrics metrics;
    std::vector<ServerSnapshot> servers;
    std::vector<EventRecord> events;
    SimulationInvariants invariants;
};

[[nodiscard]] std::string to_string(QueueDiscipline discipline);
[[nodiscard]] std::string to_string(EventType type);
[[nodiscard]] QueueDiscipline parse_queue_discipline(const std::string& value);
void validate_config(const SimulationConfig& config);

}  // namespace queueforge
