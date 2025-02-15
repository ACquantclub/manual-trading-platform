#pragma once
#include "Types.h"
#include "Order.h"
#include "OrderBook.h"
#include "Position.h"
#include "Trade.h"
#include <map>
#include <unordered_map>
#include <vector>
#include <memory>

namespace trading {

class Market {
public:
    // Order Processing
    void addOrder(const Order& order);
    void cancelOrder(const OrderId& orderId);

    // Market Data Queries
    bool hasOrderBook(const Symbol& symbol) const;
    const OrderBook& getOrderBook(const Symbol& symbol) const;
    OrderBook& getOrderBook(const Symbol& symbol);
    std::vector<Trade> getTradesForSymbol(const Symbol& symbol) const;

    // Position tracking
    Position& getPosition(const Symbol& symbol);
    const Position& getPosition(const Symbol& symbol) const;
    std::vector<Position> getAllPositions() const;
    
    // Order matching
    std::vector<Trade> matchOrders(const Symbol& symbol);

private:
    // Map of symbol to order book
    std::unordered_map<Symbol, std::unique_ptr<OrderBook>> order_books_;
    
    // Map of symbol to position
    std::unordered_map<Symbol, std::unique_ptr<Position>> positions_;
    
    // Trade history
    std::unordered_map<Symbol, std::vector<Trade>> trades_;
    
    // Helper methods
    OrderBook& getOrCreateOrderBook(const Symbol& symbol);
    Position& getOrCreatePosition(const Symbol& symbol);
};

}