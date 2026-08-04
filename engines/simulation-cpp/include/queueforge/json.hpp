#pragma once

#include <cstddef>
#include <map>
#include <stdexcept>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

namespace queueforge {

class JsonError final : public std::runtime_error {
public:
    JsonError(std::size_t position, std::string message);
    [[nodiscard]] std::size_t position() const noexcept;

private:
    std::size_t position_;
};

class JsonValue {
public:
    using Object = std::map<std::string, JsonValue, std::less<>>;
    using Array = std::vector<JsonValue>;
    using Storage = std::variant<std::nullptr_t, bool, double, std::string, Array, Object>;

    JsonValue();
    JsonValue(std::nullptr_t);
    JsonValue(bool value);
    JsonValue(double value);
    JsonValue(int value);
    JsonValue(std::string value);
    JsonValue(const char* value);
    JsonValue(Array value);
    JsonValue(Object value);

    [[nodiscard]] bool is_null() const noexcept;
    [[nodiscard]] bool is_bool() const noexcept;
    [[nodiscard]] bool is_number() const noexcept;
    [[nodiscard]] bool is_string() const noexcept;
    [[nodiscard]] bool is_array() const noexcept;
    [[nodiscard]] bool is_object() const noexcept;

    [[nodiscard]] bool as_bool() const;
    [[nodiscard]] double as_number() const;
    [[nodiscard]] const std::string& as_string() const;
    [[nodiscard]] const Array& as_array() const;
    [[nodiscard]] const Object& as_object() const;
    [[nodiscard]] Array& as_array();
    [[nodiscard]] Object& as_object();

    [[nodiscard]] const JsonValue& at(std::string_view key) const;
    [[nodiscard]] bool contains(std::string_view key) const;

    [[nodiscard]] const Storage& storage() const noexcept;

private:
    Storage storage_;
};

[[nodiscard]] JsonValue parse_json(std::string_view text);
[[nodiscard]] std::string dump_json(const JsonValue& value, bool pretty = false);

}  // namespace queueforge
