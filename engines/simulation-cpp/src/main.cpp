#include "queueforge/health.hpp"
#include "queueforge/json.hpp"
#include "queueforge/json_io.hpp"
#include "queueforge/simulator.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

struct Arguments {
    bool health = false;
    bool pretty = false;
    bool validate_only = false;
    std::string input_path;
    std::string output_path;
};

Arguments parse_arguments(int argc, char* argv[]) {
    Arguments arguments;

    for (int index = 1; index < argc; ++index) {
        const std::string_view argument{argv[index]};

        if (argument == "--health") {
            arguments.health = true;
        } else if (argument == "--pretty") {
            arguments.pretty = true;
        } else if (argument == "--validate-only") {
            arguments.validate_only = true;
        } else if (argument == "--input") {
            if (++index >= argc) {
                throw std::invalid_argument("--input requires a path");
            }
            arguments.input_path = argv[index];
        } else if (argument == "--output") {
            if (++index >= argc) {
                throw std::invalid_argument("--output requires a path or '-'");
            }
            arguments.output_path = argv[index];
        } else {
            throw std::invalid_argument("unknown argument: " + std::string(argument));
        }
    }

    if (arguments.health) {
        if (argc != 2) {
            throw std::invalid_argument("--health cannot be combined with other arguments");
        }
        return arguments;
    }

    if (arguments.input_path.empty()) {
        throw std::invalid_argument("--input is required");
    }
    if (arguments.output_path.empty()) {
        throw std::invalid_argument("--output is required");
    }

    return arguments;
}

std::string read_text_file(const std::string& path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {
        throw std::invalid_argument("unable to open input file: " + path);
    }

    return std::string(
        std::istreambuf_iterator<char>(stream),
        std::istreambuf_iterator<char>());
}

void write_output(const std::string& path, const std::string& content) {
    if (path == "-") {
        std::cout << content << '\n';
        return;
    }

    const std::filesystem::path destination(path);
    const std::filesystem::path temporary = destination.string() + ".tmp";

    std::error_code error;
    std::filesystem::remove(temporary, error);

    {
        std::ofstream stream(temporary, std::ios::binary | std::ios::trunc);
        if (!stream) {
            throw std::runtime_error("unable to open temporary output file: " + temporary.string());
        }

        stream << content << '\n';
        stream.flush();
        if (!stream) {
            throw std::runtime_error("failed while writing output file: " + temporary.string());
        }
    }

    std::filesystem::rename(temporary, destination, error);
    if (error) {
        std::filesystem::remove(temporary);
        throw std::runtime_error(
            "unable to replace output file '" + destination.string() + "': " + error.message());
    }
}

void print_usage() {
    std::cerr
        << "Usage:\n"
        << "  queueforge-sim --health\n"
        << "  queueforge-sim --input scenario.json --output result.json [--pretty]\n"
        << "  queueforge-sim --input scenario.json --output - --validate-only [--pretty]\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        const Arguments arguments = parse_arguments(argc, argv);

        if (arguments.health) {
            std::cout << queueforge::health_json() << '\n';
            return 0;
        }

        const queueforge::JsonValue input = queueforge::parse_json(
            read_text_file(arguments.input_path));
        const queueforge::SimulationConfig config = queueforge::config_from_json(input);

        if (arguments.validate_only) {
            write_output(
                arguments.output_path,
                queueforge::dump_json(
                    queueforge::validation_result_to_json(),
                    arguments.pretty));
            return 0;
        }

        const queueforge::SimulationResult result = queueforge::Simulator{}.run(config);
        write_output(
            arguments.output_path,
            queueforge::dump_json(queueforge::result_to_json(result), arguments.pretty));
        return 0;
    } catch (const queueforge::JsonError& error) {
        std::cerr << error.what() << '\n';
        return 65;
    } catch (const std::invalid_argument& error) {
        std::cerr << "Input error: " << error.what() << '\n';
        print_usage();
        return 65;
    } catch (const std::filesystem::filesystem_error& error) {
        std::cerr << "File-system error: " << error.what() << '\n';
        return 73;
    } catch (const std::exception& error) {
        std::cerr << "Simulation error: " << error.what() << '\n';
        return 70;
    }
}
