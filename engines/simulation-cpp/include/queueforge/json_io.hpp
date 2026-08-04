#pragma once

#include "queueforge/json.hpp"
#include "queueforge/model.hpp"

namespace queueforge {

[[nodiscard]] SimulationConfig config_from_json(const JsonValue& root);
[[nodiscard]] JsonValue result_to_json(const SimulationResult& result);
[[nodiscard]] JsonValue validation_result_to_json();

}  // namespace queueforge
