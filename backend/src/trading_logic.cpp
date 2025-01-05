#include "trading_logic.h"

std::string place_order(int user_id, double price, int quantity) {
    if (quantity > 0) {
        return "Order placed successfully!";
    } else {
        return "Invalid order quantity!";
    }
}