#include <cxxtest/TestSuite.h>
#include "core/Market.h"

class VolumeRegressionTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_HighFrequencyOrdering() {
        const int NUM_ORDERS = 10000;
        for(int i = 0; i < NUM_ORDERS; i++) {
            market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        }
        TS_ASSERT_EQUALS(market->getOrderBook("AAPL").getOrders().size(), NUM_ORDERS);
    }

    void test_MultiSymbolVolume() {
        std::vector<std::string> symbols = {"AAPL", "MSFT", "GOOG", "AMZN"};
        for(const auto& sym : symbols) {
            for(int i = 0; i < 1000; i++) {
                market->addOrder(trading::Order(sym, trading::Side::BUY, 100, {100.0}));
                market->addOrder(trading::Order(sym, trading::Side::SELL, 100, {100.0}));
            }
        }
        for(const auto& sym : symbols) {
            auto trades = market->matchOrders(sym);
            TS_ASSERT_EQUALS(trades.size(), 1000);
        }
    }
};