#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "core/Order.h"
#include "core/Trade.h"
#include "core/OrderBook.h"
#include "core/Market.h"
#include "core/Position.h"

namespace py = pybind11;
using namespace trading;

PYBIND11_MODULE(trading, m) {
    py::enum_<Side>(m, "Side")
        .value("BUY", Side::BUY)
        .value("SELL", Side::SELL);
        
    py::enum_<OrderStatus>(m, "OrderStatus")
        .value("NEW", OrderStatus::NEW)
        .value("FILLED", OrderStatus::FILLED)
        .value("CANCELLED", OrderStatus::CANCELLED)
        .value("REJECTED", OrderStatus::REJECTED);

    py::class_<Price>(m, "Price")
        .def(py::init<>())
        .def_readwrite("value", &Price::value)
        .def("__lt__", &Price::operator<)
        .def("__gt__", &Price::operator>)
        .def("__eq__", &Price::operator==)
        .def("__le__", &Price::operator<=)
        .def("__ge__", &Price::operator>=);
        
    py::class_<Order>(m, "Order")
        .def(py::init<const std::string&, Side, Quantity, Price>())
        .def("getId", &Order::getId)
        .def("getSymbol", &Order::getSymbol)
        .def("getSide", &Order::getSide)
        .def("getQuantity", &Order::getQuantity)
        .def("getPrice", &Order::getPrice)
        .def("getStatus", &Order::getStatus)
        .def("setStatus", &Order::setStatus);
        
    py::class_<Position>(m, "Position")
        .def(py::init<const std::string&>())
        .def("updatePosition", &Position::updatePosition)
        .def("getQuantity", &Position::getQuantity)
        .def("getAveragePrice", &Position::getAveragePrice)
        .def("getSymbol", &Position::getSymbol);

    py::class_<Trade>(m, "Trade")
        .def(py::init<const Order&, const Order&>())
        .def("getBuyOrderId", &Trade::getBuyOrderId)
        .def("getSellOrderId", &Trade::getSellOrderId)
        .def("getSymbol", &Trade::getSymbol)
        .def("getQuantity", &Trade::getQuantity)
        .def("getPrice", &Trade::getPrice)
        .def("getTimestamp", &Trade::getTimestamp)
        .def("getSide", &Trade::getSide);

    py::class_<Timestamp>(m, "Timestamp")
        .def(py::init([]() { return Timestamp(); }))  // Modern style
        .def("__repr__", [](const Timestamp& ts) {
            return std::to_string(ts);
        });

    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<const Symbol&>())
        .def("addOrder", &OrderBook::addOrder)
        .def("cancelOrder", &OrderBook::cancelOrder)
        .def("matchOrders", &OrderBook::matchOrders)
        .def("getSymbol", &OrderBook::getSymbol)
        .def("hasOrder", &OrderBook::hasOrder)
        .def("getOrder", &OrderBook::getOrder)
        .def("getOrders", &OrderBook::getOrders);

    py::class_<Market>(m, "Market")
        .def(py::init<>())
        .def("addOrder", &Market::addOrder)
        .def("cancelOrder", &Market::cancelOrder)
        .def("hasOrderBook", &Market::hasOrderBook)
        .def("getOrderBook", 
            py::overload_cast<const Symbol&>(&Market::getOrderBook, py::const_),
            py::return_value_policy::reference)
        .def("getOrderBook",
            py::overload_cast<const Symbol&>(&Market::getOrderBook),
            py::return_value_policy::reference)
        .def("getTradesForSymbol", &Market::getTradesForSymbol)
        .def("getPosition", py::overload_cast<const Symbol&>(&Market::getPosition, py::const_))
        .def("getAllPositions", &Market::getAllPositions)
        .def("matchOrders", &Market::matchOrders);
}