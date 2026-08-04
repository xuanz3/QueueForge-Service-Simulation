#include "queueforge/health.hpp"

#include "test_support.hpp"

#include <cstdlib>
#include <string>

int main() {
    const std::string payload = queueforge::health_json();
    QF_CHECK(payload.find(R"("status":"ready")") != std::string::npos);
    QF_CHECK(payload.find(R"("version":"0.2.0")") != std::string::npos);
    return EXIT_SUCCESS;
}
