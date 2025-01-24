#include <cxxtest/TestSuite.h>
#include "core/Market.h"

class EdgeCaseRegressionTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_ZeroQuantityOrders() {
        TS_ASSERT_THROWS(
            market->addOrder(trading::Order("AAPL", trading::Side::BUY, 0, {100.0})),
            std::invalid_argument
        );
    }

    void test_NegativePriceOrders() {
        TS_ASSERT_THROWS(
            market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {-100.0})),
            std::invalid_argument
        );
    }
};