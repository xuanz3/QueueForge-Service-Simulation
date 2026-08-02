#pragma once

#include "queueforge/model.hpp"

#include <cstddef>
#include <cstdint>
#include <deque>
#include <optional>

namespace queueforge {

class WaitingQueue {
public:
    explicit WaitingQueue(QueueDiscipline discipline);

    void push(std::uint64_t customer_id, bool priority);
    [[nodiscard]] std::optional<std::uint64_t> pop();
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;

private:
    QueueDiscipline discipline_;
    std::deque<std::uint64_t> fifo_;
    std::deque<std::uint64_t> priority_;
    std::deque<std::uint64_t> standard_;
};

}  // namespace queueforge
