#pragma once
#include <string>
#include <cstdint>

namespace trading {
    enum class Side {
        BUY,
        SELL
    };

    enum class OrderStatus {
        NEW,
        FILLED,
        CANCELLED,
        REJECTED
    };

    struct Price {
        double value;
    };

    using OrderId = std::string;
    using Quantity = double;
    using Symbol = std::string;
    using Timestamp = int64_t;
}