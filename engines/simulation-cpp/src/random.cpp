#include "queueforge/random.hpp"

#include <cmath>
#include <limits>
#include <stdexcept>

namespace queueforge {

DeterministicRandom::DeterministicRandom(std::uint64_t seed) : engine_(seed) {}

double DeterministicRandom::unit_interval() {
    constexpr double denominator = 9007199254740992.0;  // 2^53
    const std::uint64_t bits = engine_() >> 11U;
    return static_cast<double>(bits) / denominator;
}

double DeterministicRandom::exponential_minutes(double rate_per_hour) {
    if (!(rate_per_hour > 0.0) || !std::isfinite(rate_per_hour)) {
        throw std::invalid_argument("arrival rate must be finite and greater than zero");
    }

    const double rate_per_minute = rate_per_hour / 60.0;
    const double u = unit_interval();
    return -std::log1p(-u) / rate_per_minute;
}

double DeterministicRandom::triangular_minutes(const ServiceDistribution& distribution) {
    const double a = distribution.minimum_minutes;
    const double m = distribution.mode_minutes;
    const double b = distribution.maximum_minutes;

    if (!(a > 0.0) || a > m || m > b) {
        throw std::invalid_argument("invalid triangular distribution");
    }

    if (a == b) {
        return a;
    }

    const double u = unit_interval();
    const double split = (m - a) / (b - a);

    if (u < split) {
        return a + std::sqrt(u * (b - a) * (m - a));
    }

    return b - std::sqrt((1.0 - u) * (b - a) * (b - m));
}

bool DeterministicRandom::bernoulli(double probability) {
    if (probability <= 0.0) {
        return false;
    }
    if (probability >= 1.0) {
        return true;
    }
    return unit_interval() < probability;
}

}  // namespace queueforge
