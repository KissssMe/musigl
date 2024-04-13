import hashlib
import random
import sys
from utils import *
from SAMP import *
from params import *
from oracle import *


########## HELPER FUNCTIONS ##########

def tagged_hash(tag: str, msg: bytes) -> bytes:
    tag_hash = hashlib.sha512(tag.encode()).digest()
    return hashlib.sha512(tag_hash + tag_hash + msg).digest()


# 哈希函数计算输入的哈希值
def hash_function(input_data):
    hash_object = hashlib.sha512(input_data.encode())
    hash_value = int.from_bytes(hash_object.digest(), byteorder='big')
    #    truncated_hash = hash_value >> (hash_value.bit_length() - N)  # 使用位运算截断前n位
    return hash_value


# 伪随机数生成器，选择随机输入
def random_input_generator():
    random_input = random.getrandbits(128)  # 使用128位随机数
    return random_input


def count_bits(num):
    binary = bin(num)[2:]  # 将整数转换为二进制字符串，去除前缀'0b'
    count = binary.count('1')  # 统计1和0的比特数
    return count


# 还没改
# Hagg函数
def Hagg(input_data) -> Poly:
    while True:
        random_input = random_input_generator()
        output = hash_function(str(input_data) + str(random_input))
        if count_bits(output) != kappa:
            continue
        bit_list = []
        while output > 0:
            bit = output & 1  # 使用位与运算获取最低位的比特值
            bit_list.append(bit)
            output = output >> 1  # 右移1位，将下一位的比特移至最低位
        bit_list.reverse()  # 反转列表，使得最高位的比特在最前面
        a = Poly(bit_list)
        return a


# 对的
def Setup(lamda):
    global A_
    A = gen_ring_matrix(k, l)
    I = gen_identity_mat(k)
    A_ = [row_A + row_I for row_A, row_I in zip(A, I)]
    return A_


# 对的
def Gen():
    s1 = gen_small_polynomials_vec(l + k)
    A_ = Setup(1)
    t1 = ring_mat_ring_vec_mul(A_, s1, Q)
    return t1, s1

# 暂时没用到
# 遍历密钥列表，检查是否存在与给定公钥相等的密钥,如果给定公钥在列表中出现2次，则返回True
def is_second_unique_key(pk_list, public_key):
    for key in pk_list:
        if key != pk_list[0]:
            if key == public_key:
                return True
            else:
                return False
    return False


def check_existence_condition(t_list):
    t1 = t_list[0]
    for i in range(1, len(t_list)):
        if t_list[i] == t1:
            return False
    return True


def check_pk_list(t_list, pk_list) -> bool:
    for i in range(1, len(t_list)):
        if t_list[i] != pk_list[i]:
            return False
    return True


# 为keyagg函数做准备的，生成每个公钥对应肩膀上的指数
def key_agg_coeff(key_set: List[Poly], public_key: Poly) -> Poly:
    key_bytes_list = []
    for key in key_set:
        key_bytes = poly_to_bytes(key)
        key_bytes_list.append(key_bytes)
    L = tagged_hash("KeyAgg list", b''.join(key_bytes_list))
    #print(L)
    pk_bytes = poly_to_bytes(public_key)
    coefficient = H_agg(L + pk_bytes)
    #print(coefficient)
    return coefficient

def concatenate_l(list:list[list[Poly]],a2=Poly([0]),a1=b''):
    res=b''
    for i in range(n):
        for j in range(len(list[i])):
            res+=poly_to_bytes(list[i][j])
    res+=a1
    for i in range(len(a2)):
        res+=poly_to_bytes(a2[i])
    return res

def concatenate_W(list,a2=Poly([0]),a1=''):
    res=b''
    for i in range(n):
        for j in range(len(list[i][0])):
            res+=poly_to_bytes(list[i][0][j])
    res+=a1.encode()
    for i in range(len(a2)):
        res+=poly_to_bytes(a2[i])
    return res

def split_bytes(r_, m):
    length = len(r_)
    size = length // m
    return [r_[i*size:(i+1)*size] for i in range(m)]



########## MUSIGL FUNCTIONS ##########
# keyagg函数
def aggregate_public_keys(public_key_list: List[Poly]) -> Poly:
    aggregate_key = [Poly([0 for _ in range(N)])]*len(public_key_list[0])
    for t_i in public_key_list:
        a_i = H_agg(concatenate_l(public_key_list, t_i))
        #print(a_i)
        #print(t_i)
        a_i_pk = ring_vec_ring_mul(t_i,a_i,Q)
        #print(a_i_pk)
        aggregate_key = ring_vec_ring_vec_sum(aggregate_key, a_i_pk, Q)
        #print(aggregate_key)
    return aggregate_key


def aggregate(ones:list[(list[Poly], list[Poly])])->tuple[list[Poly], list[Poly]]:
    for _ in range(n):
        if ones[_][0]==False:
            return False
    sum = [Poly([0 for _ in range(N)])]*n
    for _ in range(n):
        sum = vec_vec_mul(sum, ones[_][0])
    return (ones[0][1], sum)


def sign_off(sk1 : list[Poly],pk1 : list[Poly]):
    y1_1 = []
    for i in range(l+k):
        y1_1.append(Poly(np.random.normal(0, sigma_1, N)))
    s1 = sk1
    y1 = []
    w1 = []
    y1.append(y1_1)
    for i in range(1, m):  #索引都是从0开始的！！！
        y1_i = []
        for j in range(l+k):
            y1_i.append(Poly(np.random.normal(0, sigma_y, N)))
        y1.append(y1_i)

    for j in range(0, m):
        w1_j = ring_mat_ring_vec_mul(A_,y1[j],Q)
        w1.append(w1_j)
    com1 = tuple(w1)
    off1 = (pk1, com1)
    st1 = tuple(y1 + w1)
    return off1, st1


# def sign_online(st1,sk1,msg,msgs,pk_list,t_list):
#     if not (check_pk_list(t_list,pk_list) or check_existence_condition(t_list)):
#         return None
#     key_bytes_list = []
#     for key in pk_list:
#         key_bytes = poly_to_bytes(key)
#         key_bytes_list.append(key_bytes)
#     L = tagged_hash("KeyAgg list", b''.join(key_bytes_list))
#     pk_bytes = poly_to_bytes(pk_list[0])
#     a_1 = Hagg(L + pk_bytes)
#     aggregate_pk = aggregate_public_keys(pk_list)
#     W = concatenate_msgs(msgs)

#shr后写


def sign_online(st1,sk1,msgs,miu,pk_list):
    ti = [None]*n
    com = [None]*n
    for i in range(1,n):
        #索引从1开始，因此pk_list传进来时，第一个元素是自己的公钥
        (ti[i],com[i])=msgs[i]
        if ti[i] != pk_list[i]:
            return None
        if ti[i]==pk_list[0]:
            return None
    com[0]=st1[m]
        
    L = ti.copy() 
    L[0] = pk_list[0] #加入t1
    a1=H_agg(concatenate_l(L,pk_list[0]))   #还没把hagg加进来
    t_=aggregate_public_keys(L) #假设这个函数是对的

    #question:聚合方式是一个一个还是一群一群
    W = msgs.copy() 
    W.insert(0, (pk_list[0], st1[m]))
    r_=H_non(concatenate_W(W,t_,miu),512)    #r为字节列表
    r=split_bytes(r_,m-1)

    b=[Poly([0])]*(m-1)
    for j in range(m-1):
        b[j]=SAMP(r[j])
    b.insert(0, Poly([1]))
    w=[Poly([0])]*m
    for j in range(m):
        for k in range(n):
            w[j]=ring_sum(w[j],com[k][j],Q)

    w_=ring_vec_ring_vec_mul(b,w,Q)
    y1=st1.copy()[:m]
    y1_=ring_vec_ring_vec_mul(b,y1,Q)
    c=H_sig(concatenate_l(w_,t_,miu))
    v=ring_mul(ring_mul(c,a1,Q),sk1,Q)
    z1=ring_sum(v,y1_,Q)
    if RejSamp(v,z1,b)==0:
        z1=None
    on1=(z1,w_)
    return on1


        

def concatenate_msgs(msgs):
    concatenated_msgs = ""
    for t, com in msgs:
        concatenated_msgs += poly_to_bytes(t) + poly_to_bytes(com)
    return concatenated_msgs


def verify_sig(aggregate_pk_bytes: Poly, msg: bytes, sig_bytes: bytes) -> bool:
    sig = bytes_to_poly(sig_bytes)
    w, z = sig
    t = bytes_to_poly(aggregate_pk_bytes)
    c = Hagg(w + msg + t)
    left = ring_vec_ring_vec_sum(ring_mat_ring_vec_mul(A_, z, Q), -ring_mul(c, t, Q), Q)
    right = w

    B = sigma_1*math.sqrt(N*(l+k))
    B_n = B*math.sqrt(n)
    if left == right and L2_norm(z) <= B_n:
        return True
    else:
        return False


# a = Poly([1]*512)
# b=Poly([2, 2])
# #print(Hagg('1'))
# print(aggregate_public_keys([a, a]))
    
if __name__=="__main__":
    pk1,sk1=Gen()
    pk2,sk2=Gen()
    pk3,sk3=Gen()
    print(pk1)
    print(pk2)
    print(pk3)

