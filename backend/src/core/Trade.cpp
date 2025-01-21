#include "core/Trade.h"
#include <chrono>
#include <stdexcept>

namespace trading {

Trade::Trade(const Order& buyOrder, const Order& sellOrder) 
    : buy_order_id_(buyOrder.getId())
    , sell_order_id_(sellOrder.getId())
    , symbol_(buyOrder.getSymbol())
    , quantity_(buyOrder.getQuantity())
    , price_(buyOrder.getPrice())
    , timestamp_(std::chrono::system_clock::now().time_since_epoch().count())
{
    if (buyOrder.getSymbol() != sellOrder.getSymbol()) {
        throw std::invalid_argument("Orders must have matching symbols");
    }
    if (buyOrder.getSide() != Side::BUY || sellOrder.getSide() != Side::SELL) {
        throw std::invalid_argument("Invalid order sides for trade");
    }
    if (buyOrder.getPrice().value < sellOrder.getPrice().value) {
        throw std::invalid_argument("Buy price must be >= sell price");
    }
}
}