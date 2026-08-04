#pragma once

#include "queueforge/model.hpp"

namespace queueforge {

class Simulator {
public:
    [[nodiscard]] SimulationResult run(const SimulationConfig& config) const;
};

}  // namespace queueforge
