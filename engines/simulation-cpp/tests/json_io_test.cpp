#include "queueforge/json.hpp"
#include "queueforge/json_io.hpp"
#include "queueforge/simulator.hpp"

#include "test_support.hpp"

#include <cstdlib>

int main() {
    const auto input = queueforge::parse_json(R"({
      "schemaVersion": "1.0",
      "simulation": {"durationMinutes": 480, "seed": 20260801},
      "arrivals": {"type": "poisson", "ratePerHour": 24},
      "service": {
        "type": "triangular",
        "minimumMinutes": 3,
        "modeMinutes": 6,
        "maximumMinutes": 12
      },
      "queue": {
        "discipline": "priority_fifo",
        "serverCount": 4,
        "priorityCustomerRatio": 0.15
      }
    })");

    const queueforge::SimulationConfig config = queueforge::config_from_json(input);
    QF_CHECK(config.server_count == 4);
    QF_CHECK(config.seed == 20260801);
    QF_CHECK(config.discipline == queueforge::QueueDiscipline::PriorityFifo);

    const queueforge::SimulationResult result = queueforge::Simulator{}.run(config);
    const std::string output =
        queueforge::dump_json(queueforge::result_to_json(result), false);
    const auto parsed_output = queueforge::parse_json(output);

    QF_CHECK(parsed_output.at("schemaVersion").as_string() == "1.0");
    QF_CHECK(parsed_output.at("engineVersion").as_string() == "0.2.0");
    QF_CHECK(parsed_output.at("invariants").at("accountingBalanced").as_bool());
    QF_CHECK(parsed_output.at("metrics").at("arrived").as_number() > 0.0);

    return EXIT_SUCCESS;
}
