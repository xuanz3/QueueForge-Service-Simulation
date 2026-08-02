#include "queueforge/simulator.hpp"

#include "test_support.hpp"

#include <cstdlib>

namespace {

queueforge::SimulationConfig demo_config() {
    return queueforge::SimulationConfig{
        480.0,
        20260801,
        24.0,
        queueforge::ServiceDistribution{3.0, 6.0, 12.0},
        queueforge::QueueDiscipline::PriorityFifo,
        4,
        0.15,
    };
}

}  // namespace

int main() {
    const queueforge::Simulator simulator;
    const queueforge::SimulationResult first = simulator.run(demo_config());
    const queueforge::SimulationResult second = simulator.run(demo_config());

    QF_CHECK(first.metrics.arrived == second.metrics.arrived);
    QF_CHECK(first.metrics.completed == second.metrics.completed);
    QF_CHECK(first.metrics.maximum_queue_length == second.metrics.maximum_queue_length);
    QF_CHECK(approximately_equal(
        first.metrics.average_wait_minutes,
        second.metrics.average_wait_minutes));
    QF_CHECK(approximately_equal(
        first.metrics.overall_utilisation,
        second.metrics.overall_utilisation));
    QF_CHECK(first.events.size() == second.events.size());

    QF_CHECK(first.metrics.arrived > 0);
    QF_CHECK(first.metrics.completed <= first.metrics.arrived);
    QF_CHECK(first.invariants.accounting_balanced);
    QF_CHECK(first.invariants.utilisation_within_range);
    QF_CHECK(first.invariants.chronology_valid);
    QF_CHECK(first.metrics.overall_utilisation >= 0.0);
    QF_CHECK(first.metrics.overall_utilisation <= 1.0);
    QF_CHECK(first.servers.size() == 4);

    queueforge::SimulationConfig overloaded = demo_config();
    overloaded.server_count = 1;
    overloaded.arrival_rate_per_hour = 60.0;
    const queueforge::SimulationResult congested = simulator.run(overloaded);
    QF_CHECK(congested.metrics.maximum_queue_length > 0);
    QF_CHECK(congested.metrics.waiting_at_end > 0);
    QF_CHECK(congested.invariants.accounting_balanced);

    bool invalid_rejected = false;
    try {
        queueforge::SimulationConfig invalid = demo_config();
        invalid.service.minimum_minutes = 8.0;
        invalid.service.mode_minutes = 6.0;
        static_cast<void>(simulator.run(invalid));
    } catch (const std::invalid_argument&) {
        invalid_rejected = true;
    }
    QF_CHECK(invalid_rejected);

    return EXIT_SUCCESS;
}
