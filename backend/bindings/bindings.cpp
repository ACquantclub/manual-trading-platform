#include <pybind11/pybind11.h>
#include "core/Order.h"
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
        .def_readwrite("value", &Price::value);
        
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
}