#include <cxxtest/TestSuite.h>
#include "core/Market.h"

class OrderBookSystemTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

    void setupBasicMarket() {
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        market->addOrder(trading::Order("AAPL", trading::Side::SELL, 100, {150.0}));
        market->addOrder(trading::Order("MSFT", trading::Side::BUY, 200, {250.0}));
        market->addOrder(trading::Order("MSFT", trading::Side::SELL, 200, {250.0}));
    }

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_MultipleOrderBooks() {
        setupBasicMarket();
        
        TS_ASSERT(market->hasOrderBook("AAPL"));
        TS_ASSERT(market->hasOrderBook("MSFT"));
        
        const auto& appleBook = market->getOrderBook("AAPL");
        const auto& msftBook = market->getOrderBook("MSFT");
        
        TS_ASSERT_EQUALS(appleBook.getOrders().size(), 2);
        TS_ASSERT_EQUALS(msftBook.getOrders().size(), 2);
    }

    void test_OrderBookPriority() {
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {151.0}));
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        
        const auto& book = market->getOrderBook("AAPL");
        auto orders = book.getOrders();
        
        TS_ASSERT_EQUALS(orders[0].getPrice().value, 150.0);
    }
};