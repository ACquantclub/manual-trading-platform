#include "core/Market.h"
#include <stdexcept>

namespace trading {

OrderBook& Market::getOrCreateOrderBook(const Symbol& symbol) {
    auto it = order_books_.find(symbol);
    if (it == order_books_.end()) {
        auto [inserted_it, success] = order_books_.emplace(symbol, std::make_unique<OrderBook>(symbol));
        return *inserted_it->second;
    }
    return *it->second;
}

Position& Market::getOrCreatePosition(const Symbol& symbol) {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        auto [inserted_it, success] = positions_.emplace(symbol, std::make_unique<Position>(symbol));
        return *inserted_it->second;
    }
    return *it->second;
}

void Market::addOrder(const Order& order) {
    // Validate order parameters
    if (order.getQuantity() <= 0) {
        throw std::invalid_argument("Order quantity must be greater than 0");
    }
    if (order.getPrice().value <= 0.0) {
        throw std::invalid_argument("Order price must be greater than 0");
    }
    if (order.getSymbol().empty()) {
        throw std::invalid_argument("Order symbol cannot be empty");
    }

    auto& orderbook = getOrCreateOrderBook(order.getSymbol());
    orderbook.addOrder(order);
}

void Market::cancelOrder(const OrderId& orderId) {
    for (auto& [symbol, orderbook] : order_books_) {
        if (orderbook->hasOrder(orderId)) {
            orderbook->cancelOrder(orderId);
            return;
        }
    }
    throw std::invalid_argument("Order not found");
}

bool Market::hasOrderBook(const Symbol& symbol) const {
    return order_books_.find(symbol) != order_books_.end();
}

const OrderBook& Market::getOrderBook(const Symbol& symbol) const {
    auto it = order_books_.find(symbol);
    if (it == order_books_.end()) {
        throw std::invalid_argument("OrderBook not found for symbol");
    }
    return *it->second;
}

std::vector<Trade> Market::getTradesForSymbol(const Symbol& symbol) const {
    auto it = trades_.find(symbol);
    if (it == trades_.end()) {
        return std::vector<Trade>();
    }
    return it->second;
}

Position& Market::getPosition(const Symbol& symbol) {
    return getOrCreatePosition(symbol);
}

const Position& Market::getPosition(const Symbol& symbol) const {
    auto it = positions_.find(symbol);
    if (it == positions_.end()) {
        throw std::invalid_argument("Position not found for symbol");
    }
    return *it->second;
}

std::vector<Position> Market::getAllPositions() const {
    std::vector<Position> positions;
    for (const auto& [symbol, position] : positions_) {
        positions.push_back(*position);
    }
    return positions;
}

std::vector<Trade> Market::matchOrders(const Symbol& symbol) {
    auto& orderbook = getOrCreateOrderBook(symbol);
    auto new_trades = orderbook.matchOrders();
    
    // Update positions and trade history
    for (const auto& trade : new_trades) {
        auto& position = getOrCreatePosition(symbol);
        // Create buy and sell orders using correct constructor
        Order buyOrder(symbol, Side::BUY, trade.getQuantity(), trade.getPrice());
        Order sellOrder(symbol, Side::SELL, trade.getQuantity(), trade.getPrice());
        
        position.updatePosition(buyOrder);
        position.updatePosition(sellOrder);
        
        trades_[symbol].push_back(trade);
    }
    
    return new_trades;
}

}