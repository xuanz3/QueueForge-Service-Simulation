#include "queueforge/json_io.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace queueforge {
namespace {

const JsonValue::Object& required_object(const JsonValue& parent, std::string_view key) {
    return parent.at(key).as_object();
}

double required_number(const JsonValue& parent, std::string_view key) {
    return parent.at(key).as_number();
}

std::string required_string(const JsonValue& parent, std::string_view key) {
    return parent.at(key).as_string();
}

std::uint64_t required_uint64(const JsonValue& parent, std::string_view key) {
    const double value = required_number(parent, key);
    if (!std::isfinite(value) || value < 0.0 || std::floor(value) != value ||
        value > static_cast<double>(std::numeric_limits<std::uint64_t>::max())) {
        throw std::invalid_argument(std::string(key) + " must be a non-negative integer");
    }
    return static_cast<std::uint64_t>(value);
}

std::size_t required_size(const JsonValue& parent, std::string_view key) {
    const std::uint64_t value = required_uint64(parent, key);
    if (value > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        throw std::invalid_argument(std::string(key) + " is too large");
    }
    return static_cast<std::size_t>(value);
}

JsonValue::Object event_to_object(const EventRecord& event) {
    JsonValue::Object object{
        {"customerId", static_cast<double>(event.customer_id)},
        {"priority", event.priority},
        {"queueLengthAfter", static_cast<double>(event.queue_length_after)},
        {"timeMinutes", event.time_minutes},
        {"type", to_string(event.type)},
    };

    if (event.server_id.has_value()) {
        object.emplace("serverId", static_cast<double>(*event.server_id));
    } else {
        object.emplace("serverId", JsonValue(nullptr));
    }

    return object;
}

}  // namespace

SimulationConfig config_from_json(const JsonValue& root) {
    if (!root.is_object()) {
        throw std::invalid_argument("simulation input must be a JSON object");
    }

    if (required_string(root, "schemaVersion") != "1.0") {
        throw std::invalid_argument("schemaVersion must be '1.0'");
    }

    const JsonValue simulation(required_object(root, "simulation"));
    const JsonValue arrivals(required_object(root, "arrivals"));
    const JsonValue service(required_object(root, "service"));
    const JsonValue queue(required_object(root, "queue"));

    if (required_string(arrivals, "type") != "poisson") {
        throw std::invalid_argument("arrivals.type must be 'poisson'");
    }
    if (required_string(service, "type") != "triangular") {
        throw std::invalid_argument("service.type must be 'triangular'");
    }

    SimulationConfig config;
    config.duration_minutes = required_number(simulation, "durationMinutes");
    config.seed = required_uint64(simulation, "seed");
    config.arrival_rate_per_hour = required_number(arrivals, "ratePerHour");
    config.service = ServiceDistribution{
        required_number(service, "minimumMinutes"),
        required_number(service, "modeMinutes"),
        required_number(service, "maximumMinutes"),
    };
    config.discipline = parse_queue_discipline(required_string(queue, "discipline"));
    config.server_count = required_size(queue, "serverCount");
    config.priority_customer_ratio = required_number(queue, "priorityCustomerRatio");

    validate_config(config);
    return config;
}

JsonValue result_to_json(const SimulationResult& result) {
    JsonValue::Array servers;
    servers.reserve(result.servers.size());
    for (const ServerSnapshot& server : result.servers) {
        servers.emplace_back(JsonValue::Object{
            {"busyMinutes", server.busy_minutes},
            {"id", static_cast<double>(server.id)},
            {"utilisation", server.utilisation},
        });
    }

    JsonValue::Array events;
    events.reserve(result.events.size());
    for (const EventRecord& event : result.events) {
        events.emplace_back(event_to_object(event));
    }

    const SimulationMetrics& metrics = result.metrics;

    return JsonValue::Object{
        {"discipline", to_string(result.discipline)},
        {"durationMinutes", result.duration_minutes},
        {"engineVersion", result.engine_version},
        {"events", std::move(events)},
        {"invariants",
         JsonValue::Object{
             {"accountingBalanced", result.invariants.accounting_balanced},
             {"chronologyValid", result.invariants.chronology_valid},
             {"utilisationWithinRange", result.invariants.utilisation_within_range},
         }},
        {"metrics",
         JsonValue::Object{
             {"arrived", static_cast<double>(metrics.arrived)},
             {"averageQueueLength", metrics.average_queue_length},
             {"averageWaitMinutes", metrics.average_wait_minutes},
             {"completed", static_cast<double>(metrics.completed)},
             {"inServiceAtEnd", static_cast<double>(metrics.in_service_at_end)},
             {"maximumQueueLength", static_cast<double>(metrics.maximum_queue_length)},
             {"maximumWaitMinutes", metrics.maximum_wait_minutes},
             {"medianWaitMinutes", metrics.median_wait_minutes},
             {"overallUtilisation", metrics.overall_utilisation},
             {"p95WaitMinutes", metrics.p95_wait_minutes},
             {"throughputPerHour", metrics.throughput_per_hour},
             {"waitingAtEnd", static_cast<double>(metrics.waiting_at_end)},
         }},
        {"schemaVersion", result.schema_version},
        {"seed", static_cast<double>(result.seed)},
        {"servers", std::move(servers)},
    };
}

JsonValue validation_result_to_json() {
    return JsonValue::Object{
        {"schemaVersion", "1.0"},
        {"status", "valid"},
    };
}

}  // namespace queueforge
