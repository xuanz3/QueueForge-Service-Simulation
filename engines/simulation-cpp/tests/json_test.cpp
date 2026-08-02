#include "queueforge/json.hpp"

#include "test_support.hpp"

#include <cstdlib>
#include <string>

int main() {
    using queueforge::JsonValue;

    const JsonValue value = queueforge::parse_json(
        R"({"message":"Queue\u0046orge","values":[1,true,null],"nested":{"x":2.5}})");

    QF_CHECK(value.at("message").as_string() == "QueueForge");
    QF_CHECK(value.at("values").as_array().size() == 3);
    QF_CHECK(value.at("values").as_array().at(1).as_bool());
    QF_CHECK(value.at("values").as_array().at(2).is_null());
    QF_CHECK(approximately_equal(value.at("nested").at("x").as_number(), 2.5));

    const std::string compact = queueforge::dump_json(value, false);
    const JsonValue reparsed = queueforge::parse_json(compact);
    QF_CHECK(reparsed.at("message").as_string() == "QueueForge");

    bool duplicate_rejected = false;
    try {
        static_cast<void>(queueforge::parse_json(R"({"a":1,"a":2})"));
    } catch (const queueforge::JsonError&) {
        duplicate_rejected = true;
    }
    QF_CHECK(duplicate_rejected);

    return EXIT_SUCCESS;
}
