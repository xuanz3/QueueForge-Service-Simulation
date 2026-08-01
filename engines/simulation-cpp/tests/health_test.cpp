#include "queueforge/health.hpp"
#include <cstdlib>
#include <string>
int main() {
    const std::string payload = queueforge::health_json();
    return payload.find("\"status\":\"ready\"") == std::string::npos ? EXIT_FAILURE : EXIT_SUCCESS;
}
