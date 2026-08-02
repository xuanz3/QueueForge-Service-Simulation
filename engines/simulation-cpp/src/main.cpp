#include "queueforge/health.hpp"
#include <iostream>
#include <string_view>
int main(int argc, char* argv[]) {
    if (argc == 2 && std::string_view{argv[1]} == "--health") { std::cout << queueforge::health_json() << '\n'; return 0; }
    std::cerr << "Usage: queueforge-sim --health\n"; return 64;
}
