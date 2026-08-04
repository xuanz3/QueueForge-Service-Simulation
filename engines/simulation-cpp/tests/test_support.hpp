#pragma once

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>

#define QF_CHECK(condition)                                                      \
    do {                                                                         \
        if (!(condition)) {                                                      \
            std::cerr << __FILE__ << ':' << __LINE__                             \
                      << " check failed: " #condition << '\n';                    \
            return EXIT_FAILURE;                                                 \
        }                                                                        \
    } while (false)

inline bool approximately_equal(double left, double right, double tolerance = 1e-9) {
    return std::fabs(left - right) <= tolerance;
}
