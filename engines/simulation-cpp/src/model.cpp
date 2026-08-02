#include "queueforge/model.hpp"

#include <cmath>
#include <stdexcept>

namespace queueforge {

std::string to_string(QueueDiscipline discipline) {
    switch (discipline) {
        case QueueDiscipline::Fifo:
            return "fifo";
        case QueueDiscipline::PriorityFifo:
            return "priority_fifo";
    }
    throw std::logic_error("unknown queue discipline");
}

std::string to_string(EventType type) {
    switch (type) {
        case EventType::Arrival:
            return "arrival";
        case EventType::ServiceStart:
            return "service_start";
        case EventType::ServiceComplete:
            return "service_complete";
    }
    throw std::logic_error("unknown event type");
}

QueueDiscipline parse_queue_discipline(const std::string& value) {
    if (value == "fifo") {
        return QueueDiscipline::Fifo;
    }
    if (value == "priority_fifo") {
        return QueueDiscipline::PriorityFifo;
    }
    throw std::invalid_argument("queue.discipline must be 'fifo' or 'priority_fifo'");
}

void validate_config(const SimulationConfig& config) {
    if (!std::isfinite(config.duration_minutes) ||
        config.duration_minutes < 60.0 ||
        config.duration_minutes > 1440.0) {
        throw std::invalid_argument("simulation.durationMinutes must be between 60 and 1440");
    }

    if (!std::isfinite(config.arrival_rate_per_hour) ||
        config.arrival_rate_per_hour <= 0.0 ||
        config.arrival_rate_per_hour > 500.0) {
        throw std::invalid_argument("arrivals.ratePerHour must be greater than 0 and at most 500");
    }

    const auto& service = config.service;
    if (!std::isfinite(service.minimum_minutes) ||
        !std::isfinite(service.mode_minutes) ||
        !std::isfinite(service.maximum_minutes) ||
        service.minimum_minutes <= 0.0 ||
        service.mode_minutes <= 0.0 ||
        service.maximum_minutes <= 0.0) {
        throw std::invalid_argument("service times must be finite and greater than 0");
    }

    if (service.minimum_minutes > service.mode_minutes ||
        service.mode_minutes > service.maximum_minutes) {
        throw std::invalid_argument(
            "service times must satisfy minimumMinutes <= modeMinutes <= maximumMinutes");
    }

    if (config.server_count < 1 || config.server_count > 20) {
        throw std::invalid_argument("queue.serverCount must be between 1 and 20");
    }

    if (!std::isfinite(config.priority_customer_ratio) ||
        config.priority_customer_ratio < 0.0 ||
        config.priority_customer_ratio > 1.0) {
        throw std::invalid_argument("queue.priorityCustomerRatio must be between 0 and 1");
    }
}

}  // namespace queueforge
