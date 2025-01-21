#include <cxxtest/TestSuite.h>
#include "core/Trade.h"
#include "core/Order.h"

class TradeTestSuite : public CxxTest::TestSuite {
private:
    trading::Order* buyOrder;
    trading::Order* sellOrder;
    trading::Trade* trade;

public:
    void setUp() {
        buyOrder = new trading::Order("AAPL", trading::Side::BUY, 100, {150.5});
        sellOrder = new trading::Order("AAPL", trading::Side::SELL, 100, {150.5});
        trade = new trading::Trade(*buyOrder, *sellOrder);
    }

    void tearDown() {
        delete trade;
        delete buyOrder;
        delete sellOrder;
    }

    void test_TradeCreation() {
        TS_ASSERT_EQUALS(trade->getSymbol(), "AAPL");
        TS_ASSERT_EQUALS(trade->getQuantity(), 100);
        TS_ASSERT_EQUALS(trade->getPrice().value, 150.5);
        TS_ASSERT_EQUALS(trade->getBuyOrderId(), buyOrder->getId());
        TS_ASSERT_EQUALS(trade->getSellOrderId(), sellOrder->getId());
    }

    void test_SymbolMismatch() {
        trading::Order buyOrderMSFT("MSFT", trading::Side::BUY, 100, {150.5});
        trading::Order sellOrderAAPL("AAPL", trading::Side::SELL, 100, {150.5});
        
        TS_ASSERT_THROWS(trading::Trade(buyOrderMSFT, sellOrderAAPL), 
                        std::invalid_argument);
    }

    void test_InvalidSides() {
        trading::Order buyOrder1("AAPL", trading::Side::BUY, 100, {150.5});
        trading::Order buyOrder2("AAPL", trading::Side::BUY, 100, {150.5});
        
        TS_ASSERT_THROWS(trading::Trade(buyOrder1, buyOrder2), 
                        std::invalid_argument);
    }

    void test_PriceValidation() {
        trading::Order buyOrderLow("AAPL", trading::Side::BUY, 100, {150.0});
        trading::Order sellOrderHigh("AAPL", trading::Side::SELL, 100, {151.0});
        
        TS_ASSERT_THROWS(trading::Trade(buyOrderLow, sellOrderHigh), 
                        std::invalid_argument);
    }

    void test_Getters() {
        TS_ASSERT(!trade->getBuyOrderId().empty());
        TS_ASSERT(!trade->getSellOrderId().empty());
        TS_ASSERT_EQUALS(trade->getSymbol(), "AAPL");
        TS_ASSERT_EQUALS(trade->getQuantity(), 100);
        TS_ASSERT_EQUALS(trade->getPrice().value, 150.5);
    }

    void test_TradeTimestamp() {
        auto beforeCreation = std::chrono::system_clock::now().time_since_epoch().count();
        trading::Trade newTrade(*buyOrder, *sellOrder);
        auto afterCreation = std::chrono::system_clock::now().time_since_epoch().count();
        
        TS_ASSERT(newTrade.getTimestamp() >= beforeCreation);
        TS_ASSERT(newTrade.getTimestamp() <= afterCreation);
    }
};