#include <cudaq.h>
#include <cudaq/algorithm.h>

#include <map>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

__qpu__ void bell_kernel(int n_qubits) {
    cudaq::qvector q(n_qubits);
    h(q[0]);
    for (int i = 0; i < n_qubits - 1; i++)
        x<cudaq::ctrl>(q[i], q[i + 1]);
    mz(q);
}

std::map<std::string, int> sample_bell(int n_qubits, int shots) {
    auto result = cudaq::sample(shots, bell_kernel, n_qubits);
    std::map<std::string, int> counts;
    for (auto &[bitstring, count] : result)
        counts[bitstring] = static_cast<int>(count);
    return counts;
}


namespace py = pybind11;

PYBIND11_MODULE(compute_dla, m) {
    m.doc() = "CUDA-Q accelerated DLA computation";
    m.def("sample_bell", &sample_bell,
          py::arg("n_qubits"), py::arg("shots") = 1000,
          "Sample a Bell state circuit and return bitstring -> count dict");
}
