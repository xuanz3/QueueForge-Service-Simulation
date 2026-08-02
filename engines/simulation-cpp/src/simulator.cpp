#include "queueforge/simulator.hpp"

#include "queueforge/random.hpp"
#include "queueforge/waiting_queue.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <limits>
#include <optional>
#include <queue>
#include <stdexcept>
#include <utility>
#include <vector>

namespace queueforge {
namespace {

enum class ScheduledEventType {
    Arrival,
    ServiceComplete,
};

struct ScheduledEvent {
    double time = 0.0;
    ScheduledEventType type = ScheduledEventType::Arrival;
    std::uint64_t customer_id = 0;
    std::size_t server_id = 0;
    std::uint64_t sequence = 0;
};

int event_rank(ScheduledEventType type) {
    switch (type) {
        case ScheduledEventType::ServiceComplete:
            return 0;
        case ScheduledEventType::Arrival:
            return 1;
    }
    return 2;
}

struct ScheduledEventLater {
    bool operator()(const ScheduledEvent& left, const ScheduledEvent& right) const noexcept {
        if (left.time != right.time) {
            return left.time > right.time;
        }

        const int left_rank = event_rank(left.type);
        const int right_rank = event_rank(right.type);
        if (left_rank != right_rank) {
            return left_rank > right_rank;
        }

        return left.sequence > right.sequence;
    }
};

struct MutableServer {
    std::size_t id = 0;
    bool busy = false;
    std::uint64_t customer_id = 0;
    double busy_until = 0.0;
    double busy_minutes = 0.0;
};

double percentile_nearest_rank(std::vector<double> values, double percentile) {
    if (values.empty()) {
        return 0.0;
    }

    std::sort(values.begin(), values.end());
    const double rank = std::ceil(percentile * static_cast<double>(values.size()));
    const std::size_t index =
        static_cast<std::size_t>(std::max(1.0, rank)) - static_cast<std::size_t>(1);
    return values.at(std::min(index, values.size() - 1));
}

double median(std::vector<double> values) {
    if (values.empty()) {
        return 0.0;
    }

    std::sort(values.begin(), values.end());
    const std::size_t middle = values.size() / 2;
    if (values.size() % 2 == 1) {
        return values[middle];
    }
    return (values[middle - 1] + values[middle]) / 2.0;
}

bool chronology_is_valid(const std::vector<Customer>& customers) {
    constexpr double epsilon = 1e-9;

    for (const Customer& customer : customers) {
        if (customer.service_start_time.has_value() &&
            *customer.service_start_time + epsilon < customer.arrival_time) {
            return false;
        }

        if (customer.service_complete_time.has_value()) {
            if (!customer.service_start_time.has_value()) {
                return false;
            }
            if (*customer.service_complete_time + epsilon < *customer.service_start_time) {
                return false;
            }
        }
    }

    return true;
}

}  // namespace

SimulationResult Simulator::run(const SimulationConfig& config) const {
    validate_config(config);

    DeterministicRandom random(config.seed);
    WaitingQueue waiting_queue(config.discipline);

    std::priority_queue<
        ScheduledEvent,
        std::vector<ScheduledEvent>,
        ScheduledEventLater>
        schedule;

    std::vector<Customer> customers;
    customers.reserve(static_cast<std::size_t>(
        std::ceil(config.arrival_rate_per_hour * config.duration_minutes / 60.0 * 1.5)));

    std::vector<MutableServer> servers;
    servers.reserve(config.server_count);
    for (std::size_t index = 0; index < config.server_count; ++index) {
        servers.push_back(MutableServer{index + 1, false, 0, 0.0, 0.0});
    }

    std::vector<EventRecord> event_log;
    std::vector<double> waits;
    std::uint64_t sequence = 0;
    std::uint64_t next_customer_id = 0;
    std::size_t completed = 0;
    std::size_t maximum_queue_length = 0;
    double queue_area = 0.0;
    double last_accounted_time = 0.0;

    auto schedule_arrival = [&](double time) {
        schedule.push(ScheduledEvent{
            time,
            ScheduledEventType::Arrival,
            0,
            0,
            sequence++,
        });
    };

    const double first_arrival = random.exponential_minutes(config.arrival_rate_per_hour);
    if (first_arrival <= config.duration_minutes) {
        schedule_arrival(first_arrival);
    }

    auto find_free_server = [&servers]() -> MutableServer* {
        for (MutableServer& server : servers) {
            if (!server.busy) {
                return &server;
            }
        }
        return nullptr;
    };

    auto customer_by_id = [&customers](std::uint64_t id) -> Customer& {
        if (id == 0 || id > customers.size()) {
            throw std::logic_error("customer identifier is outside the simulation state");
        }
        return customers.at(static_cast<std::size_t>(id - 1));
    };

    std::function<void(std::uint64_t, MutableServer&, double)> start_service;
    start_service = [&](std::uint64_t customer_id, MutableServer& server, double time) {
        Customer& customer = customer_by_id(customer_id);
        if (customer.service_start_time.has_value()) {
            throw std::logic_error("customer service started more than once");
        }

        customer.service_start_time = time;
        const double wait = std::max(0.0, time - customer.arrival_time);
        waits.push_back(wait);

        const double service_minutes = random.triangular_minutes(config.service);
        const double complete_time = time + service_minutes;

        server.busy = true;
        server.customer_id = customer_id;
        server.busy_until = complete_time;
        server.busy_minutes +=
            std::max(0.0, std::min(complete_time, config.duration_minutes) - time);

        event_log.push_back(EventRecord{
            EventType::ServiceStart,
            time,
            customer_id,
            server.id,
            customer.priority,
            waiting_queue.size(),
        });

        schedule.push(ScheduledEvent{
            complete_time,
            ScheduledEventType::ServiceComplete,
            customer_id,
            server.id,
            sequence++,
        });
    };

    while (!schedule.empty()) {
        const ScheduledEvent event = schedule.top();
        if (event.time > config.duration_minutes) {
            break;
        }
        schedule.pop();

        if (event.time + 1e-12 < last_accounted_time) {
            throw std::logic_error("event schedule moved backwards in time");
        }

        queue_area +=
            static_cast<double>(waiting_queue.size()) * (event.time - last_accounted_time);
        last_accounted_time = event.time;

        if (event.type == ScheduledEventType::Arrival) {
            const std::uint64_t customer_id = ++next_customer_id;
            const bool priority = random.bernoulli(config.priority_customer_ratio);
            customers.push_back(Customer{
                customer_id,
                priority,
                event.time,
                std::nullopt,
                std::nullopt,
            });

            event_log.push_back(EventRecord{
                EventType::Arrival,
                event.time,
                customer_id,
                std::nullopt,
                priority,
                waiting_queue.size(),
            });

            if (MutableServer* server = find_free_server(); server != nullptr) {
                start_service(customer_id, *server, event.time);
            } else {
                waiting_queue.push(customer_id, priority);
                maximum_queue_length = std::max(maximum_queue_length, waiting_queue.size());
                event_log.back().queue_length_after = waiting_queue.size();
            }

            const double next_arrival =
                event.time + random.exponential_minutes(config.arrival_rate_per_hour);
            if (next_arrival <= config.duration_minutes) {
                schedule_arrival(next_arrival);
            }
            continue;
        }

        if (event.server_id == 0 || event.server_id > servers.size()) {
            throw std::logic_error("service completion references an unknown server");
        }

        MutableServer& server = servers.at(event.server_id - 1);
        if (!server.busy || server.customer_id != event.customer_id) {
            throw std::logic_error("service completion does not match server state");
        }

        Customer& customer = customer_by_id(event.customer_id);
        customer.service_complete_time = event.time;
        ++completed;

        server.busy = false;
        server.customer_id = 0;
        server.busy_until = event.time;

        event_log.push_back(EventRecord{
            EventType::ServiceComplete,
            event.time,
            event.customer_id,
            event.server_id,
            customer.priority,
            waiting_queue.size(),
        });

        if (const std::optional<std::uint64_t> next = waiting_queue.pop();
            next.has_value()) {
            start_service(*next, server, event.time);
        }

        event_log.back().queue_length_after = waiting_queue.size();
    }

    if (last_accounted_time < config.duration_minutes) {
        queue_area += static_cast<double>(waiting_queue.size()) *
                      (config.duration_minutes - last_accounted_time);
    }

    std::size_t in_service_at_end = 0;
    double total_busy_minutes = 0.0;
    std::vector<ServerSnapshot> server_snapshots;
    server_snapshots.reserve(servers.size());

    bool utilisation_within_range = true;
    for (const MutableServer& server : servers) {
        if (server.busy) {
            ++in_service_at_end;
        }

        const double utilisation = server.busy_minutes / config.duration_minutes;
        if (utilisation < -1e-12 || utilisation > 1.0 + 1e-12) {
            utilisation_within_range = false;
        }

        total_busy_minutes += server.busy_minutes;
        server_snapshots.push_back(ServerSnapshot{
            server.id,
            server.busy_minutes,
            std::clamp(utilisation, 0.0, 1.0),
        });
    }

    double total_wait = 0.0;
    double maximum_wait = 0.0;
    for (const double wait : waits) {
        total_wait += wait;
        maximum_wait = std::max(maximum_wait, wait);
    }

    const std::size_t arrived = customers.size();
    const std::size_t waiting_at_end = waiting_queue.size();
    const bool accounting_balanced =
        arrived == completed + waiting_at_end + in_service_at_end;

    SimulationMetrics metrics;
    metrics.arrived = arrived;
    metrics.completed = completed;
    metrics.waiting_at_end = waiting_at_end;
    metrics.in_service_at_end = in_service_at_end;
    metrics.average_wait_minutes =
        waits.empty() ? 0.0 : total_wait / static_cast<double>(waits.size());
    metrics.median_wait_minutes = median(waits);
    metrics.p95_wait_minutes = percentile_nearest_rank(waits, 0.95);
    metrics.maximum_wait_minutes = maximum_wait;
    metrics.average_queue_length = queue_area / config.duration_minutes;
    metrics.maximum_queue_length = maximum_queue_length;
    metrics.throughput_per_hour =
        static_cast<double>(completed) * 60.0 / config.duration_minutes;
    metrics.overall_utilisation =
        total_busy_minutes /
        (config.duration_minutes * static_cast<double>(config.server_count));

    SimulationResult result;
    result.seed = config.seed;
    result.duration_minutes = config.duration_minutes;
    result.discipline = config.discipline;
    result.metrics = metrics;
    result.servers = std::move(server_snapshots);
    result.events = std::move(event_log);
    result.invariants = SimulationInvariants{
        accounting_balanced,
        utilisation_within_range,
        chronology_is_valid(customers),
    };
    return result;
}

}  // namespace queueforge
