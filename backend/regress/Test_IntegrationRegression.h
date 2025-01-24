#include <cxxtest/TestSuite.h>
#include "core/Market.h"
#include "core/OrderBook.h"
#include "core/Position.h"

class IntegrationRegressionTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_OrderBookPositionIntegration() {
        // Add orders
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        market->addOrder(trading::Order("AAPL", trading::Side::SELL, 50, {150.0}));
        
        // Match orders
        auto trades = market->matchOrders("AAPL");
        TS_ASSERT_EQUALS(trades.size(), 1);
        
        // Verify position
        auto position = market->getPosition("AAPL");
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
        
        // Verify order book
        auto& book = market->getOrderBook("AAPL");
        TS_ASSERT_EQUALS(book.getOrders().size(), 1);
    }
};