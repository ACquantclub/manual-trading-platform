#include <cxxtest/TestSuite.h>
#include "core/Market.h"

class MarketLoadTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_HighFrequencyOrders() {
        const int NUM_ORDERS = 1000;
        for(int i = 0; i < NUM_ORDERS; i++) {
            market->addOrder(trading::Order("AAPL", trading::Side::BUY, 
                100, {150.0 + (i % 10)}));
        }
        
        auto trades = market->matchOrders("AAPL");
        TS_ASSERT(market->getOrderBook("AAPL").getOrders().size() > 0);
    }

    void test_MultiSymbolLoad() {
        const std::vector<std::string> symbols = {"AAPL", "MSFT", "GOOG", "AMZN"};
        for(const auto& sym : symbols) {
            for(int i = 0; i < 100; i++) {
                market->addOrder(trading::Order(sym, trading::Side::BUY, 
                    100, {100.0 + i}));
                market->addOrder(trading::Order(sym, trading::Side::SELL, 
                    100, {101.0 + i}));
            }
        }

        for(const auto& sym : symbols) {
            market->matchOrders(sym);
            TS_ASSERT(market->hasOrderBook(sym));
        }
    }
};