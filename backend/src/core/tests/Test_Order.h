#include <cxxtest/TestSuite.h>
#include "core/Order.h"
#include <set>

class OrderTestSuite : public CxxTest::TestSuite {
private:
    trading::Order* testOrder;

public:
    void setUp() {
        testOrder = new trading::Order("AAPL", trading::Side::BUY, 100, {150.5});
    }

    void tearDown() {
        delete testOrder;
    }

    void test_OrderCreation() {
        TS_ASSERT_EQUALS(testOrder->getSymbol(), "AAPL");
        TS_ASSERT_EQUALS(testOrder->getSide(), trading::Side::BUY);
        TS_ASSERT_EQUALS(testOrder->getQuantity(), 100);
        TS_ASSERT_EQUALS(testOrder->getPrice().value, 150.5);
        TS_ASSERT_EQUALS(testOrder->getStatus(), trading::OrderStatus::NEW);
    }

    void test_OrderIdUniqueness() {
        std::set<trading::OrderId> orderIds;
        const int numOrders = 100;
        
        for(int i = 0; i < numOrders; ++i) {
            trading::Order order("AAPL", trading::Side::BUY, 100, {150.5});
            orderIds.insert(order.getId());
        }
        
        TS_ASSERT_EQUALS(orderIds.size(), numOrders);
    }

    void test_OrderStatusUpdate() {
        TS_ASSERT_EQUALS(testOrder->getStatus(), trading::OrderStatus::NEW);
        
        testOrder->setStatus(trading::OrderStatus::FILLED);
        TS_ASSERT_EQUALS(testOrder->getStatus(), trading::OrderStatus::FILLED);
        
        testOrder->setStatus(trading::OrderStatus::CANCELLED);
        TS_ASSERT_EQUALS(testOrder->getStatus(), trading::OrderStatus::CANCELLED);
    }

    void test_OrderTimestamp() {
        auto beforeCreation = std::chrono::system_clock::now().time_since_epoch().count();
        trading::Order order("AAPL", trading::Side::BUY, 100, {150.5});
        auto afterCreation = std::chrono::system_clock::now().time_since_epoch().count();
        
        TS_ASSERT(beforeCreation > 0);
        TS_ASSERT(afterCreation > beforeCreation);
    }

    void test_Getters() {
        trading::Order order("MSFT", trading::Side::SELL, 200, {250.75});
        
        TS_ASSERT(!order.getId().empty());
        TS_ASSERT_EQUALS(order.getSymbol(), "MSFT");
        TS_ASSERT_EQUALS(order.getSide(), trading::Side::SELL);
        TS_ASSERT_EQUALS(order.getQuantity(), 200);
        TS_ASSERT_EQUALS(order.getPrice().value, 250.75);
    }
};