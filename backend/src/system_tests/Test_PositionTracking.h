#include <cxxtest/TestSuite.h>
#include "core/Market.h"
#include <algorithm>

class PositionTrackingSystemTestSuite : public CxxTest::TestSuite {
private:
    trading::Market* market;

    void setupBasicMarket() {
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        market->addOrder(trading::Order("AAPL", trading::Side::SELL, 100, {150.0}));
        market->addOrder(trading::Order("MSFT", trading::Side::BUY, 200, {250.0}));
        market->addOrder(trading::Order("MSFT", trading::Side::SELL, 200, {250.0}));
    }

    const trading::Position* findPosition(const std::vector<trading::Position>& positions, 
                                       const std::string& symbol) {
        auto it = std::find_if(positions.begin(), positions.end(),
            [&symbol](const trading::Position& pos) { return pos.getSymbol() == symbol; });
        return it != positions.end() ? &(*it) : nullptr;
    }

public:
    void setUp() { market = new trading::Market(); }
    void tearDown() { delete market; }

    void test_MultiSymbolPositions() {
        setupBasicMarket();
        
        market->matchOrders("AAPL");
        market->matchOrders("MSFT");
        
        auto positions = market->getAllPositions();
        TS_ASSERT_EQUALS(positions.size(), 2);

        const auto* applePos = findPosition(positions, "AAPL");
        const auto* msftPos = findPosition(positions, "MSFT");
        
        TS_ASSERT(applePos != nullptr);
        TS_ASSERT(msftPos != nullptr);
        TS_ASSERT_EQUALS(applePos->getQuantity(), 0);
        TS_ASSERT_EQUALS(msftPos->getQuantity(), 0);
    }

    void test_PositionAccumulation() {
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        market->addOrder(trading::Order("AAPL", trading::Side::BUY, 100, {150.0}));
        market->addOrder(trading::Order("AAPL", trading::Side::SELL, 150, {150.0}));
        
        market->matchOrders("AAPL");
        
        const auto& position = market->getPosition("AAPL");
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
    }
};