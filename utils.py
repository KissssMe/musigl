from hashlib import shake_256
from typing import List

import numpy as np
from numpy.polynomial import Polynomial as Poly
from numpy.polynomial.polynomial import polydiv

from params import *

#对的
def gen_small_polynomials_vec(vec_size: int) -> List[Poly]:
    vec = []
    gen_range = int(eta)
    for i in range(vec_size):
        vec.append(Poly(np.random.randint(low=-gen_range, high=gen_range, size=N)))
    return vec

#对的
def gen_ring_vec(vec_size: int) -> List[Poly]:
    vec = []
    gen_range = int(2 ** GAMMA)
    for i in range(vec_size):
        vec.append(Poly(np.random.randint(low=-gen_range, high=gen_range, size=N)))
        vec[i].coef %= Q
    return vec

#对的
def gen_ring_matrix(row_size: int, col_size: int) -> List[List[Poly]]:
    ring_matrix = []
    for _ in range(row_size):
        row = gen_ring_vec(col_size)
        ring_matrix.append(row)
    return ring_matrix

#对的
def gen_identity_mat(dim: int) -> List[List[Poly]]:
    identity_mat = []
    for i in range(dim):
        row = []
        for j in range(dim):
            if i == j:
                row.append(Poly(1))
            else:
                row.append(Poly(0))
        identity_mat.append(row)
    return identity_mat

#对的
def random_ring_vec() -> List[Poly]:
    vec = []
    for i in range(M):
        # Gaussian distribution
        generated = np.random.normal(0, SIGMA, size=N).astype(int)
        generated %= Q
        vec.append(Poly(generated))
    return vec

#对的
def ring_sum(a: Poly, b: Poly, mod: int) -> Poly:
    result = a+b
    result.coef = [coef % mod for coef in result.coef]
    return result

#对的
def ring_mul(a: Poly, b: Poly, mod: int) -> Poly:
    if not isinstance(a, Poly) or not isinstance(b, Poly):
        raise TypeError("输入必须是Polynomial对象")
    cyclotomics = Poly([1] + [0] * (N - 1) + [1])
    mul=a*b
    _, r = polydiv(mul.coef, cyclotomics.coef)
    # r_=Poly(mul.coef)%Poly(cyclotomics.coef)
    # r=r_.coef
    result = [coef % mod for coef in r]
    return Poly(result)

#对的
def ring_vec_ring_mul(ring_vec: List[Poly], ring: Poly, mod: int) -> List[Poly]:
    result_ring_vec = []
    for i in range(len(ring_vec)):
        poly_factor = ring_mul(ring_vec[i], ring, mod)
        for i in range(len(poly_factor.coef)):
            poly_factor.coef[i] %= mod
        #poly_factor.coef %= mod
        result_ring_vec.append(poly_factor)
    return result_ring_vec

#对的
def ring_mat_ring_vec_mul(ring_mat: List[List[Poly]], ring_vec: List[Poly], mod: int) -> List[Poly]:
    result_ring_vec = []
    for i in range(len(ring_mat)):
        poly_factor = Poly([0 for _ in range(len(ring_vec[0].coef))])
        for j in range(len(ring_vec)):
            poly_factor += ring_mul(ring_mat[i][j], ring_vec[j], mod)
        poly_factor.coef %= mod
        result_ring_vec.append(poly_factor)
    return result_ring_vec

#对的
def ring_vec_ring_vec_mul(a: List[Poly], b: List[Poly], mod: int) -> Poly:
    ring = Poly([0 for _ in range(N)])
    for i in range(len(a)):
        poly_factor = ring_mul(a[i], b[i], mod)
        ring = ring_sum(ring, poly_factor, mod)
    return ring

#对的
def ring_vec_ring_vec_sum(a: List[Poly], b: List[Poly], mod: int) -> List[Poly]:
    res = []
    for i in range(len(a)):
        res.append(ring_sum(a[i], b[i], mod))
    return res

def ring_vec_ring_vec_sub(a: List[Poly], b: List[Poly], mod: int) -> List[Poly]:
    res = []
    for i in range(len(a)):
        res.append(ring_sum(a[i], -b[i], mod))
    return res

#对的
def scalar_vec_mul(vec: Poly, scalar: int, mod: int):
    ring_copy = vec.copy()
    for i in range(N):
        ring_copy.coef[i] = ring_copy.coef[i] * scalar % mod
    return ring_copy


def scalar_vec_add(vec: Poly, scalar: int, mod: int):
    ring_copy = vec.copy()
    for i in range(N):
        ring_copy.coef[i] = ring_copy.coef[i] + scalar % mod
    return ring_copy


def scalar_mat_ring_vec_mul(scalar_mat: List[List[float]], ring_vec: List[Poly], mod: int) -> List[Poly]:
    result_ring_vec = []
    for i in scalar_mat:
        tmp = Poly([0] * N)
        for _, j in enumerate(i):
            tmp += j * ring_vec[_]
        result_ring_vec.append(tmp)
    return result_ring_vec


def L2_norm(ring_vec: List[Poly])->float:
    norm = []
    for i in ring_vec:
        sum = 0
        for j in range(N):
            sum += ring_vec[i].coef[j]**2
        norm.append(sum)
    return sum(norm)


def lift(ring_vec: List[Poly], ring: Poly) -> List[Poly]:
    ring_copy = ring.copy()
    ring_copy = scalar_vec_mul(ring_copy, -2)
    ring_copy = scalar_vec_add(ring_copy, Q)
    ring_copy.coef %= 2 * Q
    ring_vec_copy = ring_vec.copy()
    for i in range(len(ring_vec_copy)):
        ring_vec_copy[i] = scalar_vec_mul(ring_vec_copy[i], 2)
        ring_vec_copy[i].coef %= 2 * Q
    return ring_vec_copy + [ring_copy]


def h_one(
        big_l: List[Poly],
        big_h_2q: List[Poly],
        message: bytes,
        first: Poly,
        second: Poly,
) -> bytes:
    shake = shake_256()
    for pub_key in big_l:
        shake.update(pub_key.coef)
    shake.update(message)
    for i in range(M):
        shake.update(big_h_2q[i].coef)
    shake.update(first.coef)
    shake.update(second.coef)
    return shake.digest(int(N * L / 8))

#错的代码
# def bytes_to_poly(input_bytes: bytes) -> Poly:
#     bits = []
#     ring = []
#     for i in range(len(input_bytes)):
#         bits += [1 if input_bytes[i] & (1 << n) else 0 for n in range(8)]
#     for i in range(N):
#         ring.append(sum([bits[j + i * L] * (2 ** j) for j in range(L)]))
#     return Poly(ring)


# def poly_to_bytes(poly: Poly) -> bytes:
#     bits = []
#     result_bytes = bytearray(b"")
#     for i in range(N):
#         bits += [1 if int(poly.coef[i]) & (1 << n) else 0 for n in range(L)]
#     for i in range(int(N * L / 8)):
#         result_bytes.append(sum([bits[j + i * 8] * (2 ** j) for j in range(8)]))
#     return bytes(result_bytes)


def flatten(array_of_arrays: List[List]) -> List:
    result = []
    for array in array_of_arrays:
        for item in array:
            result.append(item)
    return result


def unflatten(array: List, split_at: int) -> List[List]:
    array_of_arrays = []
    part = []
    for i in range(len(array)):
        part.append(array[i])
        if (i + 1) % split_at == 0:
            array_of_arrays.append(part)
            part = []
    return array_of_arrays


#对的
def vec_vec_mul(a: List[Poly], b: List[Poly]) -> Poly:
    ring = Poly([0 for _ in range(N)])
    for i in range(len(a)):
        poly_factor = a[i]+b[i]
        ring = ring + poly_factor
    return ring


def poly_to_bytes(poly: Poly) -> bytes:
    coef_bytes = np.array(poly.coef).tobytes()
    return coef_bytes

def bytes_to_poly(bytes_obj: bytes) -> Poly:
    remainder = len(bytes_obj) % 8
    if remainder:  # if the bytes_obj is not a multiple of 8
        bytes_obj = bytes_obj[:-remainder]  # remove the extra bytes
    coef = np.frombuffer(bytes_obj, dtype=np.float64)
    poly = Poly(coef)
    return poly


if __name__=="__main__":
    p = [Poly([1, 2, 3, 4])]*3
    a=[Poly([2,1,3,4])]*3
    b=ring_vec_ring_vec_sub(p,a,Q)
    print(b[0].coef)