#include <cxxtest/TestSuite.h>
#include "core/Market.h"

class MarketTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

    trading::Order createBuyOrder(const std::string& symbol = "AAPL", 
                                double price = 100.0, 
                                int quantity = 100) {
        return trading::Order(symbol, trading::Side::BUY, quantity, {price});
    }

    trading::Order createSellOrder(const std::string& symbol = "AAPL", 
                                 double price = 100.0, 
                                 int quantity = 100) {
        return trading::Order(symbol, trading::Side::SELL, quantity, {price});
    }

public:
    void setUp() {
        market = new trading::Market();
    }

    void tearDown() {
        delete market;
    }

    void test_OrderBookCreation() {
        TS_ASSERT(!market->hasOrderBook("AAPL"));
        market->addOrder(createBuyOrder("AAPL"));
        TS_ASSERT(market->hasOrderBook("AAPL"));
    }

    void test_AddOrder() {
        auto order = createBuyOrder();
        market->addOrder(order);
        TS_ASSERT(market->getOrderBook("AAPL").hasOrder(order.getId()));
    }

    void test_CancelOrder() {
        auto order = createBuyOrder();
        market->addOrder(order);
        market->cancelOrder(order.getId());
        TS_ASSERT(!market->getOrderBook("AAPL").hasOrder(order.getId()));
    }

    void test_CancelNonexistentOrder() {
        TS_ASSERT_THROWS(market->cancelOrder("nonexistent"), std::invalid_argument);
    }

    void test_MultipleSymbols() {
        market->addOrder(createBuyOrder("AAPL"));
        market->addOrder(createBuyOrder("MSFT"));
        TS_ASSERT(market->hasOrderBook("AAPL"));
        TS_ASSERT(market->hasOrderBook("MSFT"));
    }

    void test_OrderMatching() {
        market->addOrder(createBuyOrder("AAPL", 100.0));
        market->addOrder(createSellOrder("AAPL", 100.0));
        
        auto trades = market->matchOrders("AAPL");
        TS_ASSERT_EQUALS(trades.size(), 1);
        TS_ASSERT_EQUALS(market->getTradesForSymbol("AAPL").size(), 1);
    }

    void test_PositionTracking() {
        market->addOrder(createBuyOrder("AAPL", 100.0));
        market->addOrder(createSellOrder("AAPL", 100.0));
        market->matchOrders("AAPL");
        
        const auto& position = market->getPosition("AAPL");
        TS_ASSERT_EQUALS(position.getSymbol(), "AAPL");
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
    }

    void test_MultiplePositions() {
        // Add matching orders for AAPL
        market->addOrder(createBuyOrder("AAPL", 100.0));
        market->addOrder(createSellOrder("AAPL", 100.0));
        
        // Add matching orders for MSFT
        market->addOrder(createBuyOrder("MSFT", 100.0));
        market->addOrder(createSellOrder("MSFT", 100.0));
        
        // Execute trades for both symbols
        market->matchOrders("AAPL");
        market->matchOrders("MSFT");
        
        auto positions = market->getAllPositions();
        TS_ASSERT_EQUALS(positions.size(), 2);
    }

    void test_GetNonexistentOrderBook() {
        const trading::Market* const_market = market;
        TS_ASSERT_THROWS(const_market->getOrderBook("INVALID"), std::invalid_argument);
    }

    void test_TradeHistory() {
        TS_ASSERT(market->getTradesForSymbol("AAPL").empty());
        
        market->addOrder(createBuyOrder("AAPL", 100.0));
        market->addOrder(createSellOrder("AAPL", 100.0));
        market->matchOrders("AAPL");
        
        TS_ASSERT_EQUALS(market->getTradesForSymbol("AAPL").size(), 1);
    }

    void test_NoMatchingOrders() {
        market->addOrder(createBuyOrder("AAPL", 90.0));
        market->addOrder(createSellOrder("AAPL", 100.0));
        
        auto trades = market->matchOrders("AAPL");
        TS_ASSERT_EQUALS(trades.size(), 0);
    }
};