#include "queueforge/json.hpp"

#include <charconv>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>
#include <utility>

namespace queueforge {
namespace {

class Parser {
public:
    explicit Parser(std::string_view text) : text_(text) {}

    JsonValue parse() {
        skip_whitespace();
        JsonValue value = parse_value();
        skip_whitespace();
        if (!eof()) {
            fail("unexpected trailing content");
        }
        return value;
    }

private:
    std::string_view text_;
    std::size_t pos_ = 0;

    [[nodiscard]] bool eof() const noexcept {
        return pos_ >= text_.size();
    }

    [[nodiscard]] char peek() const {
        if (eof()) {
            throw JsonError(pos_, "unexpected end of input");
        }
        return text_[pos_];
    }

    char take() {
        const char c = peek();
        ++pos_;
        return c;
    }

    [[noreturn]] void fail(std::string message) const {
        throw JsonError(pos_, std::move(message));
    }

    void skip_whitespace() {
        while (!eof()) {
            const char c = text_[pos_];
            if (c == ' ' || c == '\n' || c == '\r' || c == '\t') {
                ++pos_;
            } else {
                break;
            }
        }
    }

    JsonValue parse_value() {
        skip_whitespace();
        if (eof()) {
            fail("expected a JSON value");
        }

        switch (peek()) {
            case '{':
                return parse_object();
            case '[':
                return parse_array();
            case '"':
                return JsonValue(parse_string());
            case 't':
                consume_literal("true");
                return JsonValue(true);
            case 'f':
                consume_literal("false");
                return JsonValue(false);
            case 'n':
                consume_literal("null");
                return JsonValue(nullptr);
            default:
                if (peek() == '-' || (peek() >= '0' && peek() <= '9')) {
                    return JsonValue(parse_number());
                }
                fail("invalid JSON value");
        }
    }

    void consume_literal(std::string_view literal) {
        if (text_.substr(pos_, literal.size()) != literal) {
            fail("invalid literal");
        }
        pos_ += literal.size();
    }

    JsonValue parse_object() {
        JsonValue::Object object;
        take();  // {
        skip_whitespace();

        if (!eof() && peek() == '}') {
            take();
            return JsonValue(std::move(object));
        }

        while (true) {
            skip_whitespace();
            if (peek() != '"') {
                fail("object key must be a string");
            }

            std::string key = parse_string();
            skip_whitespace();
            if (take() != ':') {
                fail("expected ':' after object key");
            }

            JsonValue value = parse_value();
            const auto [it, inserted] = object.emplace(std::move(key), std::move(value));
            static_cast<void>(it);
            if (!inserted) {
                fail("duplicate object key");
            }

            skip_whitespace();
            const char separator = take();
            if (separator == '}') {
                break;
            }
            if (separator != ',') {
                fail("expected ',' or '}' in object");
            }
        }

        return JsonValue(std::move(object));
    }

    JsonValue parse_array() {
        JsonValue::Array array;
        take();  // [
        skip_whitespace();

        if (!eof() && peek() == ']') {
            take();
            return JsonValue(std::move(array));
        }

        while (true) {
            array.push_back(parse_value());
            skip_whitespace();
            const char separator = take();
            if (separator == ']') {
                break;
            }
            if (separator != ',') {
                fail("expected ',' or ']' in array");
            }
        }

        return JsonValue(std::move(array));
    }

    std::string parse_string() {
        if (take() != '"') {
            fail("expected string");
        }

        std::string result;
        while (!eof()) {
            const char c = take();
            if (c == '"') {
                return result;
            }
            if (static_cast<unsigned char>(c) < 0x20U) {
                fail("control character in string");
            }
            if (c != '\\') {
                result.push_back(c);
                continue;
            }

            if (eof()) {
                fail("unterminated escape sequence");
            }

            const char escape = take();
            switch (escape) {
                case '"':
                case '\\':
                case '/':
                    result.push_back(escape);
                    break;
                case 'b':
                    result.push_back('\b');
                    break;
                case 'f':
                    result.push_back('\f');
                    break;
                case 'n':
                    result.push_back('\n');
                    break;
                case 'r':
                    result.push_back('\r');
                    break;
                case 't':
                    result.push_back('\t');
                    break;
                case 'u':
                    append_unicode_escape(result);
                    break;
                default:
                    fail("invalid escape sequence");
            }
        }

        fail("unterminated string");
    }

    void append_unicode_escape(std::string& output) {
        std::uint32_t codepoint = parse_hex4();

        if (codepoint >= 0xD800U && codepoint <= 0xDBFFU) {
            if (text_.substr(pos_, 2) != "\\u") {
                fail("high surrogate must be followed by a low surrogate");
            }
            pos_ += 2;
            const std::uint32_t low = parse_hex4();
            if (low < 0xDC00U || low > 0xDFFFU) {
                fail("invalid low surrogate");
            }
            codepoint = 0x10000U + ((codepoint - 0xD800U) << 10U) + (low - 0xDC00U);
        } else if (codepoint >= 0xDC00U && codepoint <= 0xDFFFU) {
            fail("unexpected low surrogate");
        }

        append_utf8(output, codepoint);
    }

    std::uint32_t parse_hex4() {
        std::uint32_t value = 0;
        for (int i = 0; i < 4; ++i) {
            if (eof()) {
                fail("incomplete unicode escape");
            }
            const char c = take();
            value <<= 4U;
            if (c >= '0' && c <= '9') {
                value |= static_cast<std::uint32_t>(c - '0');
            } else if (c >= 'a' && c <= 'f') {
                value |= static_cast<std::uint32_t>(c - 'a' + 10);
            } else if (c >= 'A' && c <= 'F') {
                value |= static_cast<std::uint32_t>(c - 'A' + 10);
            } else {
                fail("invalid hexadecimal digit");
            }
        }
        return value;
    }

    static void append_utf8(std::string& output, std::uint32_t codepoint) {
        if (codepoint <= 0x7FU) {
            output.push_back(static_cast<char>(codepoint));
        } else if (codepoint <= 0x7FFU) {
            output.push_back(static_cast<char>(0xC0U | (codepoint >> 6U)));
            output.push_back(static_cast<char>(0x80U | (codepoint & 0x3FU)));
        } else if (codepoint <= 0xFFFFU) {
            output.push_back(static_cast<char>(0xE0U | (codepoint >> 12U)));
            output.push_back(static_cast<char>(0x80U | ((codepoint >> 6U) & 0x3FU)));
            output.push_back(static_cast<char>(0x80U | (codepoint & 0x3FU)));
        } else if (codepoint <= 0x10FFFFU) {
            output.push_back(static_cast<char>(0xF0U | (codepoint >> 18U)));
            output.push_back(static_cast<char>(0x80U | ((codepoint >> 12U) & 0x3FU)));
            output.push_back(static_cast<char>(0x80U | ((codepoint >> 6U) & 0x3FU)));
            output.push_back(static_cast<char>(0x80U | (codepoint & 0x3FU)));
        } else {
            throw JsonError(0, "unicode code point out of range");
        }
    }

    double parse_number() {
        const std::size_t start = pos_;

        if (peek() == '-') {
            ++pos_;
        }

        if (eof()) {
            fail("incomplete number");
        }

        if (peek() == '0') {
            ++pos_;
        } else {
            if (peek() < '1' || peek() > '9') {
                fail("invalid number");
            }
            while (!eof() && peek() >= '0' && peek() <= '9') {
                ++pos_;
            }
        }

        if (!eof() && peek() == '.') {
            ++pos_;
            if (eof() || peek() < '0' || peek() > '9') {
                fail("fraction requires digits");
            }
            while (!eof() && peek() >= '0' && peek() <= '9') {
                ++pos_;
            }
        }

        if (!eof() && (peek() == 'e' || peek() == 'E')) {
            ++pos_;
            if (!eof() && (peek() == '+' || peek() == '-')) {
                ++pos_;
            }
            if (eof() || peek() < '0' || peek() > '9') {
                fail("exponent requires digits");
            }
            while (!eof() && peek() >= '0' && peek() <= '9') {
                ++pos_;
            }
        }

        const std::string token{text_.substr(start, pos_ - start)};
        char* end = nullptr;
        const double value = std::strtod(token.c_str(), &end);
        if (end == nullptr || *end != '\0' || !std::isfinite(value)) {
            fail("number is outside the supported range");
        }
        return value;
    }
};

void append_indent(std::string& output, int depth) {
    output.append(static_cast<std::size_t>(depth * 2), ' ');
}

void append_escaped_string(std::string& output, std::string_view value) {
    output.push_back('"');
    static constexpr char hex[] = "0123456789abcdef";

    for (const unsigned char c : value) {
        switch (c) {
            case '"':
                output += "\\\"";
                break;
            case '\\':
                output += "\\\\";
                break;
            case '\b':
                output += "\\b";
                break;
            case '\f':
                output += "\\f";
                break;
            case '\n':
                output += "\\n";
                break;
            case '\r':
                output += "\\r";
                break;
            case '\t':
                output += "\\t";
                break;
            default:
                if (c < 0x20U) {
                    output += "\\u00";
                    output.push_back(hex[(c >> 4U) & 0x0FU]);
                    output.push_back(hex[c & 0x0FU]);
                } else {
                    output.push_back(static_cast<char>(c));
                }
        }
    }

    output.push_back('"');
}

void dump_value(const JsonValue& value, std::string& output, bool pretty, int depth) {
    const auto& storage = value.storage();

    if (std::holds_alternative<std::nullptr_t>(storage)) {
        output += "null";
    } else if (const auto* boolean = std::get_if<bool>(&storage)) {
        output += *boolean ? "true" : "false";
    } else if (const auto* number = std::get_if<double>(&storage)) {
        std::ostringstream stream;
        stream << std::setprecision(std::numeric_limits<double>::max_digits10) << *number;
        output += stream.str();
    } else if (const auto* string = std::get_if<std::string>(&storage)) {
        append_escaped_string(output, *string);
    } else if (const auto* array = std::get_if<JsonValue::Array>(&storage)) {
        output.push_back('[');
        if (!array->empty()) {
            if (pretty) {
                output.push_back('\n');
            }
            for (std::size_t i = 0; i < array->size(); ++i) {
                if (pretty) {
                    append_indent(output, depth + 1);
                }
                dump_value((*array)[i], output, pretty, depth + 1);
                if (i + 1 < array->size()) {
                    output.push_back(',');
                }
                if (pretty) {
                    output.push_back('\n');
                }
            }
            if (pretty) {
                append_indent(output, depth);
            }
        }
        output.push_back(']');
    } else {
        const auto& object = std::get<JsonValue::Object>(storage);
        output.push_back('{');
        if (!object.empty()) {
            if (pretty) {
                output.push_back('\n');
            }
            std::size_t index = 0;
            for (const auto& [key, child] : object) {
                if (pretty) {
                    append_indent(output, depth + 1);
                }
                append_escaped_string(output, key);
                output += pretty ? ": " : ":";
                dump_value(child, output, pretty, depth + 1);
                if (++index < object.size()) {
                    output.push_back(',');
                }
                if (pretty) {
                    output.push_back('\n');
                }
            }
            if (pretty) {
                append_indent(output, depth);
            }
        }
        output.push_back('}');
    }
}

}  // namespace

JsonError::JsonError(std::size_t position, std::string message)
    : std::runtime_error("JSON error at byte " + std::to_string(position) + ": " + message),
      position_(position) {}

std::size_t JsonError::position() const noexcept {
    return position_;
}

JsonValue::JsonValue() : storage_(nullptr) {}
JsonValue::JsonValue(std::nullptr_t) : storage_(nullptr) {}
JsonValue::JsonValue(bool value) : storage_(value) {}
JsonValue::JsonValue(double value) : storage_(value) {}
JsonValue::JsonValue(int value) : storage_(static_cast<double>(value)) {}
JsonValue::JsonValue(std::string value) : storage_(std::move(value)) {}
JsonValue::JsonValue(const char* value) : storage_(std::string(value)) {}
JsonValue::JsonValue(Array value) : storage_(std::move(value)) {}
JsonValue::JsonValue(Object value) : storage_(std::move(value)) {}

bool JsonValue::is_null() const noexcept { return std::holds_alternative<std::nullptr_t>(storage_); }
bool JsonValue::is_bool() const noexcept { return std::holds_alternative<bool>(storage_); }
bool JsonValue::is_number() const noexcept { return std::holds_alternative<double>(storage_); }
bool JsonValue::is_string() const noexcept { return std::holds_alternative<std::string>(storage_); }
bool JsonValue::is_array() const noexcept { return std::holds_alternative<Array>(storage_); }
bool JsonValue::is_object() const noexcept { return std::holds_alternative<Object>(storage_); }

bool JsonValue::as_bool() const {
    if (!is_bool()) {
        throw std::invalid_argument("JSON value is not a boolean");
    }
    return std::get<bool>(storage_);
}

double JsonValue::as_number() const {
    if (!is_number()) {
        throw std::invalid_argument("JSON value is not a number");
    }
    return std::get<double>(storage_);
}

const std::string& JsonValue::as_string() const {
    if (!is_string()) {
        throw std::invalid_argument("JSON value is not a string");
    }
    return std::get<std::string>(storage_);
}

const JsonValue::Array& JsonValue::as_array() const {
    if (!is_array()) {
        throw std::invalid_argument("JSON value is not an array");
    }
    return std::get<Array>(storage_);
}

const JsonValue::Object& JsonValue::as_object() const {
    if (!is_object()) {
        throw std::invalid_argument("JSON value is not an object");
    }
    return std::get<Object>(storage_);
}

JsonValue::Array& JsonValue::as_array() {
    if (!is_array()) {
        throw std::invalid_argument("JSON value is not an array");
    }
    return std::get<Array>(storage_);
}

JsonValue::Object& JsonValue::as_object() {
    if (!is_object()) {
        throw std::invalid_argument("JSON value is not an object");
    }
    return std::get<Object>(storage_);
}

const JsonValue& JsonValue::at(std::string_view key) const {
    const auto& object = as_object();
    const auto it = object.find(key);
    if (it == object.end()) {
        throw std::invalid_argument("missing JSON property: " + std::string(key));
    }
    return it->second;
}

bool JsonValue::contains(std::string_view key) const {
    if (!is_object()) {
        return false;
    }
    return as_object().find(key) != as_object().end();
}

const JsonValue::Storage& JsonValue::storage() const noexcept {
    return storage_;
}

JsonValue parse_json(std::string_view text) {
    return Parser(text).parse();
}

std::string dump_json(const JsonValue& value, bool pretty) {
    std::string output;
    dump_value(value, output, pretty, 0);
    return output;
}

}  // namespace queueforge
