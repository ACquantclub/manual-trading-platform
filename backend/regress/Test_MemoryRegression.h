#include <cxxtest/TestSuite.h>
#include "core/Market.h"

class MemoryRegressionTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_LargeOrderDeletion() {
        const int NUM_ORDERS = 10000;
        std::vector<std::string> orderIds;
        
        for(int i = 0; i < NUM_ORDERS; i++) {
            auto order = trading::Order("AAPL", trading::Side::BUY, 100, {150.0});
            orderIds.push_back(order.getId());
            market->addOrder(order);
        }

        for(const auto& id : orderIds) {
            market->cancelOrder(id);
        }
        
        TS_ASSERT_EQUALS(market->getOrderBook("AAPL").getOrders().size(), 0);
    }
};