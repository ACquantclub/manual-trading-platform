#pragma once
#include "Types.h"
#include "Order.h"
#include <string>

namespace trading {

class Trade {
public:
    Trade(const Order& buyOrder, const Order& sellOrder);

    // Getters
    OrderId getBuyOrderId() const { return buy_order_id_; }
    OrderId getSellOrderId() const { return sell_order_id_; }
    std::string getSymbol() const { return symbol_; }
    Quantity getQuantity() const { return quantity_; }
    Price getPrice() const { return price_; }
    Timestamp getTimestamp() const { return timestamp_; }

private:
    OrderId buy_order_id_;
    OrderId sell_order_id_;
    std::string symbol_;
    Quantity quantity_;
    Price price_;
    Timestamp timestamp_;
};
}