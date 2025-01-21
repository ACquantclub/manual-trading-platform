#include <core/OrderBook.h>
#include <memory>
#include <map>
#include <unordered_map>
#include <stdexcept>
#include <algorithm>

namespace trading {

OrderBook::OrderBook(const Symbol& symbol)
    : symbol_(symbol)
{}

void OrderBook::addOrder(const Order& order) {
    auto [it, success] = orders_.emplace(order.getId(), order);
    if (!success) {
        throw std::invalid_argument("Order already exists");
    }
    Order& stored_order = it->second;
    if (order.getSide() == Side::BUY) {
        bids_.insert({order.getPrice(), std::ref(stored_order)});
    } else {
        asks_.insert({order.getPrice(), std::ref(stored_order)});
    }
}

void OrderBook::cancelOrder(const OrderId& orderId) {
    if (orders_.find(orderId) == orders_.end()) {
        throw std::invalid_argument("Order does not exist");
    }
    removeOrder(orderId);
}

void OrderBook::removeOrder(const OrderId& orderId) {
    const Order& order = orders_.at(orderId);
    if (order.getSide() == Side::BUY) {
        auto range = bids_.equal_range(order.getPrice());
        for (auto it = range.first; it != range.second; ++it) {
            if (it->second.get().getId() == orderId) {
                bids_.erase(it);
                break;
            }
        }
    } else {
        auto range = asks_.equal_range(order.getPrice());
        for (auto it = range.first; it != range.second; ++it) {
            if (it->second.get().getId() == orderId) {
                asks_.erase(it);
                break;
            }
        }
    }
    orders_.erase(orderId);
}

std::vector<Trade> OrderBook::matchOrders() {
    std::vector<Trade> new_trades;
    
    while (!bids_.empty() && !asks_.empty()) {
        auto bid_it = bids_.begin();
        auto ask_it = asks_.begin();
        
        if (bid_it->first.value < ask_it->first.value) {
            break;
        }
        
        Order& bid = bid_it->second.get();
        Order& ask = ask_it->second.get();
        
        Trade trade(bid, ask);
        new_trades.push_back(trade);
        trades_.push_back(trade);
        
        Quantity matched_qty = trade.getQuantity();
        if (bid.getQuantity() == matched_qty) {
            removeOrder(bid.getId());
        }
        if (ask.getQuantity() == matched_qty) {
            removeOrder(ask.getId());
        }
    }
    
    return new_trades;
}

bool OrderBook::hasOrder(const OrderId& orderId) const {
    return orders_.find(orderId) != orders_.end();
}

const Order& OrderBook::getOrder(const OrderId& orderId) const {
    auto it = orders_.find(orderId);
    if (it == orders_.end()) {
        throw std::invalid_argument("Order not found");
    }
    return it->second;
}

std::vector<Order> OrderBook::getOrders() const {
    std::vector<Order> all_orders;
    for (const auto& pair : orders_) {
        all_orders.push_back(pair.second);
    }
    return all_orders;
}

}