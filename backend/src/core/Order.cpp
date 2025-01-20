#include "core/Order.h"
#include <chrono>
#include <uuid/uuid.h>

namespace trading {

namespace {
std::string generateOrderId() {
    uuid_t uuid;
    uuid_generate(uuid);
    char uuid_str[37];
    uuid_unparse_lower(uuid, uuid_str);
    return std::string(uuid_str);
}
}

Order::Order(const std::string& symbol, Side side, Quantity qty, Price price)
    : symbol_(symbol)
    , side_(side)
    , quantity_(qty)
    , price_(price)
    , status_(OrderStatus::NEW)
    , id_(generateOrderId())
    , created_at_(std::chrono::system_clock::now().time_since_epoch().count())
{}

}