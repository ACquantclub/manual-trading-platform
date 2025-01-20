#include <cxxtest/TestSuite.h>
#include "core/Position.h"
#include "core/Order.h"

class PositionTestSuite : public CxxTest::TestSuite {
public:
    void testPositionCreation(void) {
        trading::Position position("AAPL");
        
        TS_ASSERT_EQUALS(position.getSymbol(), "AAPL");
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
        TS_ASSERT_EQUALS(position.getAveragePrice().value, 0.0);
    }

    void testBuyOrderUpdate(void) {
        trading::Position position("AAPL");
        trading::Order order("AAPL", trading::Side::BUY, 100, {150.5});
        order.setStatus(trading::OrderStatus::FILLED);
        
        position.updatePosition(order);
        
        TS_ASSERT_EQUALS(position.getQuantity(), 100);
        TS_ASSERT_EQUALS(position.getAveragePrice().value, 150.5);
    }

    void testSellOrderUpdate(void) {
        trading::Position position("AAPL");
        
        // First buy 100 shares
        trading::Order buy_order("AAPL", trading::Side::BUY, 100, {150.5});
        buy_order.setStatus(trading::OrderStatus::FILLED);
        position.updatePosition(buy_order);
        
        // Then sell 50 shares
        trading::Order sell_order("AAPL", trading::Side::SELL, 50, {160.0});
        sell_order.setStatus(trading::OrderStatus::FILLED);
        position.updatePosition(sell_order);
        
        TS_ASSERT_EQUALS(position.getQuantity(), 50);
        TS_ASSERT_EQUALS(position.getAveragePrice().value, 150.5);
    }

    void testAveragePriceCalculation(void) {
        trading::Position position("AAPL");
        
        // Buy 100 shares at 150.5
        trading::Order order1("AAPL", trading::Side::BUY, 100, {150.5});
        order1.setStatus(trading::OrderStatus::FILLED);
        position.updatePosition(order1);
        
        // Buy 50 more shares at 160.0
        trading::Order order2("AAPL", trading::Side::BUY, 50, {160.0});
        order2.setStatus(trading::OrderStatus::FILLED);
        position.updatePosition(order2);
        
        // Expected average price: ((100 * 150.5) + (50 * 160.0)) / 150 = 153.67
        TS_ASSERT_DELTA(position.getAveragePrice().value, 153.67, 0.01);
        TS_ASSERT_EQUALS(position.getQuantity(), 150);
    }

    void testUnfilledOrderUpdate(void) {
        trading::Position position("AAPL");
        trading::Order order("AAPL", trading::Side::BUY, 100, {150.5});
        // Note: order status remains NEW
        
        position.updatePosition(order);
        
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
        TS_ASSERT_EQUALS(position.getAveragePrice().value, 0.0);
    }

    void testSymbolMismatch(void) {
        trading::Position position("AAPL");
        trading::Order order("MSFT", trading::Side::BUY, 100, {150.5});
        order.setStatus(trading::OrderStatus::FILLED);
        
        position.updatePosition(order);
        
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
        TS_ASSERT_EQUALS(position.getAveragePrice().value, 0.0);
    }

    void testZeroQuantityReset(void) {
        trading::Position position("AAPL");
        
        trading::Order buy("AAPL", trading::Side::BUY, 100, {150.5});
        buy.setStatus(trading::OrderStatus::FILLED);
        position.updatePosition(buy);
        
        trading::Order sell("AAPL", trading::Side::SELL, 100, {160.0});
        sell.setStatus(trading::OrderStatus::FILLED);
        position.updatePosition(sell);
        
        TS_ASSERT_EQUALS(position.getQuantity(), 0);
        TS_ASSERT_EQUALS(position.getAveragePrice().value, 0.0);
    }
};