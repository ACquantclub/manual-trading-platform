#include <cxxtest/TestSuite.h>
#include "core/Market.h"
#include <stdexcept>

class ErrorConditionSystemTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() { 
        market = new trading::Market(); 
    }
    
    void tearDown() { 
        delete market; 
    }

    void test_InvalidOrderRejection() {
        // Test invalid symbol
        trading::Order emptySymbol("", trading::Side::BUY, 100, {100.0});
        TS_ASSERT_THROWS(market->getOrderBook(""), std::invalid_argument);

        // Test non-existent order book
        TS_ASSERT_THROWS(market->getOrderBook("INVALID"), std::invalid_argument);
    }

    void test_OrderCancellationErrors() {
        // Test canceling non-existent order
        TS_ASSERT_THROWS(market->cancelOrder("nonexistent"), std::invalid_argument);

        // Add and cancel real order
        trading::Order order("AAPL", trading::Side::BUY, 100, {150.0});
        market->addOrder(order);
        TS_ASSERT_THROWS_NOTHING(market->cancelOrder(order.getId()));

        // Try to cancel same order again
        TS_ASSERT_THROWS(market->cancelOrder(order.getId()), std::invalid_argument);
    }

    void test_DuplicateOrderBookErrors() {
        // Add order to create order book
        trading::Order order("AAPL", trading::Side::BUY, 100, {150.0});
        market->addOrder(order);
        TS_ASSERT(market->hasOrderBook("AAPL"));

        // Test accessing non-existent order book
        TS_ASSERT_THROWS(market->getOrderBook("INVALID"), std::invalid_argument);
    }
};