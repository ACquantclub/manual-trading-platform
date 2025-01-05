#include <pybind11/pybind11.h>
#include "trading_logic.h"

namespace py = pybind11;
namespace trading {

PYBIND11_MODULE(trading_core, m) {
    m.doc() = "Python bindings for trading core functionality";
    m.def("place_order", &place_order, "Place a trade order",
          py::arg("user_id"), py::arg("price"), py::arg("quantity"));
}

} // namespace trading
