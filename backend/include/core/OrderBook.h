#pragma once
#include "Types.h"
#include "Order.h"
#include "Trade.h"
#include <map>
#include <unordered_map>
#include <vector>
#include <memory>

namespace trading {

class OrderBook {
public:
    explicit OrderBook(const Symbol& symbol);

    // Order management
    void addOrder(const Order& order);
    void cancelOrder(const OrderId& orderId);

    // Order matching
    std::vector<Trade> matchOrders();

    // Getters
    Symbol getSymbol() const { return symbol_; }
    bool hasOrder(const OrderId& orderId) const;
    const Order& getOrder(const OrderId& orderId) const;
    std::vector<Order> getOrders() const;

private:
    // Symbol
    Symbol symbol_;


    // Order Reference Storage
    std::multimap<Price, std::reference_wrapper<Order>, std::greater<Price>> bids_;
    std::multimap<Price, std::reference_wrapper<Order>, std::less<Price>> asks_;
    
    // Primary storage - owns the orders
    std::unordered_map<OrderId, Order> orders_;

    // Historical Trades
    std::vector<Trade> trades_;

    void removeOrder(const OrderId& orderId);
    void matchOrder(const Order& bid, const Order& ask);
};

}