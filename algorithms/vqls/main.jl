using LinearAlgebra

const X  = [0.0 1.0; 1.0 0.0]
const Z  = [1.0 0.0; 0.0 -1.0]
const I2 = Matrix{Float64}(I, 2, 2)

function GateJ(n_qubits::Int, j::Int; gate::AbstractMatrix = X)
    factors = [k == j ? gate : I2 for k in 0:n_qubits-1]
    return reduce(kron, factors)
end

function build_M(n_qubits::Int; J::Float64 = 0.1)
    dim = 2^n_qubits
    Xsum = zeros(Float64, dim, dim)
    Zsum = zeros(Float64, dim, dim)

    for j in 0:n_qubits-1
        Xsum += GateJ(n_qubits, j)  # default gate = X

        if j != n_qubits - 1
            Zsum += GateJ(n_qubits, j; gate=Z) * GateJ(n_qubits, j+1; gate=Z)
        end
    end

    Zsum *= J
    return Xsum + Zsum
end

n_qubits = 10

M = build_M(n_qubits)
eigenvals = eigvals(Symmetric(M))

λmin = minimum(eigenvals)
λmax = maximum(eigenvals)

κ = 60

@variables η ζ

A0 = λmin + η - (ζ / κ)
A1 = λmax + η - ζ

system = [
    A0,
    A1
]
soln = solve(system)

println(soln)