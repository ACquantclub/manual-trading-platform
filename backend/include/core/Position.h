#pragma once
#include "Types.h"

namespace trading {

class Order;

class Position {
public:
    Position(const std::string& symbol);
    
    void updatePosition(const Order& order);
    Quantity getQuantity() const { return quantity_; }
    Price getAveragePrice() const { return avg_price_; }
    std::string getSymbol() const { return symbol_; }

private:
    std::string symbol_;
    Quantity quantity_;
    Price avg_price_;
};

}