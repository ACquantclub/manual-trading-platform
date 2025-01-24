#include <cxxtest/TestSuite.h>
#include "core/Market.h"
#include "core/Order.h"
#include "core/Trade.h"

class FullTradingSystemTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() {
        market = new trading::Market();
    }

    void tearDown() {
        delete market;
    }

    void test_CompleteTradeLifecycle() {
        // Test complete system flow
        auto buyOrder = trading::Order("AAPL", trading::Side::BUY, 100, {150.0});
        auto sellOrder = trading::Order("AAPL", trading::Side::SELL, 100, {150.0});
        
        market->addOrder(buyOrder);
        market->addOrder(sellOrder);
        
        auto trades = market->matchOrders("AAPL");
        TS_ASSERT_EQUALS(trades.size(), 1);
        
        const auto& position = market->getPosition("AAPL");
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
    }
};