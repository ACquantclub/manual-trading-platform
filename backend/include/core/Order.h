#pragma once
#include "Types.h"
#include <string>
#include <chrono>

namespace trading {

class Order {
public:
    Order(const std::string& symbol, Side side, Quantity qty, Price price);
    
    OrderId getId() const { return id_; }
    std::string getSymbol() const { return symbol_; }
    Side getSide() const { return side_; }
    Quantity getQuantity() const { return quantity_; }
    Price getPrice() const { return price_; }
    OrderStatus getStatus() const { return status_; }
    
    void setStatus(OrderStatus status) { status_ = status; }

private:
    OrderId id_;
    std::string symbol_;
    Side side_;
    Quantity quantity_;
    Price price_;
    OrderStatus status_;
    Timestamp created_at_;
};

}