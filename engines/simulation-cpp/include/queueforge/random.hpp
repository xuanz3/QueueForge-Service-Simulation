#pragma once

#include "queueforge/model.hpp"

#include <cstdint>
#include <random>

namespace queueforge {

class DeterministicRandom {
public:
    explicit DeterministicRandom(std::uint64_t seed);

    [[nodiscard]] double unit_interval();
    [[nodiscard]] double exponential_minutes(double rate_per_hour);
    [[nodiscard]] double triangular_minutes(const ServiceDistribution& distribution);
    [[nodiscard]] bool bernoulli(double probability);

private:
    std::mt19937_64 engine_;
};

}  // namespace queueforge
