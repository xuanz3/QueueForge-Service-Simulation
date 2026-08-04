#include "queueforge/waiting_queue.hpp"

namespace queueforge {

WaitingQueue::WaitingQueue(QueueDiscipline discipline) : discipline_(discipline) {}

void WaitingQueue::push(std::uint64_t customer_id, bool priority) {
    if (discipline_ == QueueDiscipline::Fifo) {
        fifo_.push_back(customer_id);
        return;
    }

    if (priority) {
        priority_.push_back(customer_id);
    } else {
        standard_.push_back(customer_id);
    }
}

std::optional<std::uint64_t> WaitingQueue::pop() {
    auto pop_front = [](std::deque<std::uint64_t>& queue) -> std::optional<std::uint64_t> {
        if (queue.empty()) {
            return std::nullopt;
        }
        const std::uint64_t id = queue.front();
        queue.pop_front();
        return id;
    };

    if (discipline_ == QueueDiscipline::Fifo) {
        return pop_front(fifo_);
    }

    if (!priority_.empty()) {
        return pop_front(priority_);
    }
    return pop_front(standard_);
}

std::size_t WaitingQueue::size() const noexcept {
    return fifo_.size() + priority_.size() + standard_.size();
}

bool WaitingQueue::empty() const noexcept {
    return size() == 0;
}

}  // namespace queueforge
