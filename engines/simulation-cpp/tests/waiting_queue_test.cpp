#include "queueforge/waiting_queue.hpp"

#include "test_support.hpp"

#include <cstdlib>

int main() {
    {
        queueforge::WaitingQueue queue(queueforge::QueueDiscipline::Fifo);
        queue.push(1, false);
        queue.push(2, true);
        queue.push(3, false);
        QF_CHECK(queue.pop() == 1);
        QF_CHECK(queue.pop() == 2);
        QF_CHECK(queue.pop() == 3);
        QF_CHECK(!queue.pop().has_value());
    }

    {
        queueforge::WaitingQueue queue(queueforge::QueueDiscipline::PriorityFifo);
        queue.push(1, false);
        queue.push(2, true);
        queue.push(3, true);
        queue.push(4, false);
        QF_CHECK(queue.pop() == 2);
        QF_CHECK(queue.pop() == 3);
        QF_CHECK(queue.pop() == 1);
        QF_CHECK(queue.pop() == 4);
    }

    return EXIT_SUCCESS;
}
