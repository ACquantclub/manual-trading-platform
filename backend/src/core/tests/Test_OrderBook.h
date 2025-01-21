#include <cxxtest/TestSuite.h>
#include "core/OrderBook.h"

class OrderBookTestSuite : public CxxTest::TestSuite {
private:
    trading::OrderBook* book;

    // Helper methods
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
        book = new trading::OrderBook("AAPL");
    }

    void tearDown() {
        delete book;
    }

    void test_OrderBookCreation() {
        TS_ASSERT_EQUALS(book->getSymbol(), "AAPL");
        TS_ASSERT(book->getOrders().empty());
    }

    void test_AddOrder() {
        auto order = createBuyOrder();
        book->addOrder(order);
        TS_ASSERT(book->hasOrder(order.getId()));
        TS_ASSERT_EQUALS(book->getOrders().size(), 1);
        
        const auto& retrieved = book->getOrder(order.getId());
        TS_ASSERT_EQUALS(retrieved.getId(), order.getId());
    }

    void test_DuplicateOrder() {
        auto order = createBuyOrder();
        book->addOrder(order);
        TS_ASSERT_THROWS(book->addOrder(order), std::invalid_argument);
    }

    void test_CancelOrder() {
        auto order = createBuyOrder();
        book->addOrder(order);
        book->cancelOrder(order.getId());
        TS_ASSERT(!book->hasOrder(order.getId()));
    }

    void test_CancelNonexistentOrder() {
        TS_ASSERT_THROWS(book->cancelOrder("nonexistent"), std::invalid_argument);
    }

    void test_BasicOrderMatch() {
        auto buy = createBuyOrder("AAPL", 100.0);
        auto sell = createSellOrder("AAPL", 100.0);
        
        book->addOrder(buy);
        book->addOrder(sell);
        
        auto trades = book->matchOrders();
        TS_ASSERT_EQUALS(trades.size(), 1);
        TS_ASSERT_EQUALS(trades[0].getBuyOrderId(), buy.getId());
        TS_ASSERT_EQUALS(trades[0].getSellOrderId(), sell.getId());
    }

    void test_NoMatch() {
        auto buy = createBuyOrder("AAPL", 90.0);
        auto sell = createSellOrder("AAPL", 100.0);
        
        book->addOrder(buy);
        book->addOrder(sell);
        
        auto trades = book->matchOrders();
        TS_ASSERT_EQUALS(trades.size(), 0);
        TS_ASSERT_EQUALS(book->getOrders().size(), 2);
    }

    void test_MultipleMatches() {
        book->addOrder(createBuyOrder("AAPL", 100.0));
        book->addOrder(createBuyOrder("AAPL", 101.0));
        book->addOrder(createSellOrder("AAPL", 99.0));
        book->addOrder(createSellOrder("AAPL", 98.0));
        
        auto trades = book->matchOrders();
        TS_ASSERT_EQUALS(trades.size(), 2);
    }

    void test_OrderRetrieval() {
        TS_ASSERT_THROWS(book->getOrder("nonexistent"), std::invalid_argument);
        
        auto order = createBuyOrder();
        book->addOrder(order);
        TS_ASSERT_EQUALS(book->getOrders().size(), 1);
        TS_ASSERT_EQUALS(book->getOrder(order.getId()).getId(), order.getId());
    }
};