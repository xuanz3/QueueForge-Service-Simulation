#include "queueforge/health.hpp"
namespace queueforge {
std::string health_json() {
    return R"({"service":"queueforge-simulation-engine","status":"ready","version":"0.2.0"})";
}
}
