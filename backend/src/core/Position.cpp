#include "core/Position.h"
#include "core/Order.h"

namespace trading {

Position::Position(const std::string& symbol)
    : symbol_(symbol)
    , quantity_(0)
    , avg_price_({0})
{}

void Position::updatePosition(const Order& order) {
    // Validate order
    if (order.getStatus() != OrderStatus::FILLED || 
        order.getSymbol() != symbol_) {
        return;
    }

    // Calculate position update
    if (order.getSide() == Side::BUY) {
        double total_value = quantity_ * avg_price_.value;
        total_value += order.getQuantity() * order.getPrice().value;
        quantity_ += order.getQuantity();
        if (quantity_ > 0) {
            avg_price_.value = total_value / quantity_;
        }
    } else { // SELL
        quantity_ -= order.getQuantity();
        // Average price stays the same on sells until position is closed
        if (quantity_ == 0) {
            avg_price_.value = 0;
        }
    }
}

}