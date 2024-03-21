N = 512
Q = 12289
L=14 #表示多项式的系数要用几位二进制数
M = 6
SIGMA = 283754
GAMMA = 13.6
l = 14 #矩阵的维数
k = 14 #矩阵的维数
POLY_BYTES = int((14 * N) / 8)
kappa = 256
eta = 5
m = 1 #这是啥？
n = 3 # 用户数量

# import math
#
# N=256   # ring dimension
# Q=2**64
# n=2**9    # # of parties n < 1/(16sigma1)
# q=2**64 # Prime modulus
# w=math.log2(q)
# m=2
#
# k=5             # height of A
# l=5             # width of A
# eta=11          # maximum infinity norm of s
# kappa=60        # max L1 norm of c
#
# sigmay=2**9/((math.pi)**(3/2)) * 2**(2/(N*k))*N**(3/2)*(k*w+1)**(1/2)
# sigmab=2**(5/2)/((math.pi)**(1/2)) * 2**(2/(N*k))*N**(3/2)*(k*w+1)**(1/2)
# sigma1=sigmab*sigmay*(N*(2*k*w+1)*(l+k))**(1/2) # sigma of y1 = target gaussian of y~ and z
# B=sigma1*(N*(l+k))**(1/2)   # max L2 norm of zi (signature share)
# Bn=n**(1/2)*B   # max L2 norm of z (combined signature)
# T=kappa**2*eta*(N*(l+k))**(1/2)
# alpha=(sigma1-1)/T
# t=(N/((math.pi-1)*math.log2(math.exp(1))))**(1/2)
# M=(t/alpha)+1/(2*(alpha**2))    # Repetitions for Rejection sampling
# #M=math.exp(M)