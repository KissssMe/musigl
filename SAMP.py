import numpy as np
from numpy.polynomial import Polynomial as Poly
from scipy.linalg import sqrtm
import math
import utils
import random
from params import *
omega = math.ceil(math.log(Q, 2))
# N=10
# Q=5
# k=3
# l = 3
# eta = 2
# kappa = 2
def compute_sigma_y()->float:
    numerator = 2**9 / (math.pi * math.sqrt(math.pi))
    exponent = 2 / (N * k)
    power = Q**(k / (l + k))
    factor = N**2 * math.sqrt((k * omega + 1) * (2 + N + math.log((l + k) * N)))
    
    sigma_y = numerator * 2**exponent * power * factor
    return sigma_y


def compute_sigma_b()->float:
    numerator = 2**(5/2) / math.sqrt(math.pi)
    exponent = 2 / (N * k)
    factor = N**(3/2) * math.sqrt(k * omega + 1)
    
    sigma_b = numerator * 2**exponent * factor
    return sigma_b


def compute_sigma_1(sigma_b, sigma_y)->float:
    factor = math.sqrt(N * (2 * k * omega + 1) * (l + k))
    sigma_1 = sigma_b * sigma_y * factor
    return sigma_1


sigma_y = compute_sigma_y()
sigma_b = compute_sigma_b()
sigma_1 = compute_sigma_1(sigma_b, sigma_y)


def compute_rho(Sigma:list[list[float]], c:list[Poly], z:list[Poly])->float:
    Sigma_sqrt = sqrtm(Sigma)
    Sigma_sqrt_inv = np.linalg.inv(Sigma_sqrt)

    l=[]
    for _ in range(k+l):
        l[_] = (z[_]-c[_])

    A = utils.L2_norm(utils.scalar_mat_ring_vec_mul(Sigma_sqrt_inv, l))
    exponent = -math.pi * A * A
    return math.e**exponent


def compute_D(Sigma:list[list[float]], c:list[Poly], Lambda:list[list[Poly]], z:list[Poly])->float:
    sum = 0
    for x in Lambda:
        sum = sum + compute_rho(Sigma, np.zeros_like(x), x)
    return compute_rho(Sigma, c, z)/sum
        

def SAMP(r:bytes)->Poly:
    random.seed(r)
    b = Poly(np.zeros(N))
    sigma_b = compute_sigma_b()
    seed_value = int.from_bytes(r, 'big')%(2**32-1)  # 将字节对象转换为整数
    np.random.seed(seed_value)
    samples = np.floor(np.abs(np.random.normal(0, sigma_b, N)))
    for _ in range(N):
        b.coef[_] = samples[_]
    return b


def RejSamp(v:list[Poly], z:list[Poly], B:list[Poly])->bool:
    sum = 0
    for i, b in enumerate(B):
        if i == 0:
            continue
        # 将多项式系数转换为矩阵
        coef = np.array(b.coef)
        sum += np.matmul(coef,coef)

    diag_element_1 = (sigma_y**2) * sum + sigma_1**2
    Sigma = np.diag([diag_element_1] * (k+l))

    rho = random.randint(0, 1)
    
    # 计算M
    T = (kappa**2) * eta * math.sqrt(N*(k+l))
    alpha = (sigma_1 - 1)/T
    t = math.sqrt(N/((math.pi-1)*math.log(math.e, 2)))
    exponent_M = t/alpha + 1/(2*(alpha**2))
    M = math.e**(exponent_M)

    diag_element_2 = sigma_1**2
    Sigma_mal = np.diag([diag_element_2] * (k+l))
    origin = Poly([0] * N)
    return 1 #后期格确定了记得删掉
    if rho < min([compute_D(Sigma_mal,[origin]*len(z) , Lambda, z)/(M*compute_D(Sigma, v, Lambda, z)), 1]):
        # Lambda 是一个格，还没有确定
        return 1
    return 0