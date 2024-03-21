import sys
import hashlib
import math
import random
from params import *

def H_agg(input_data) :
    seed=0
    for i in range(1):
        count=0
        out=[0]*N
        h=int(hashlib.sha512(str((input_data,seed)).encode()).hexdigest(),16)
        print(math.log(h,2))
        while(h!=0):
            i=h%N
            h//=N
            if(out[i]!=1 or out[i]!=-1):
                out[i]=random.choice([-1,1])
                count+=1
            if(count==kappa):
                #out_poly=Poly([i for i in out])
                return out
        seed+=1

def H_sig(input_data) :
    seed=0
    for i in range(1):
        count=0
        out=[0]*N
        h=int(hashlib.sha512(str((input_data,seed)).encode()).hexdigest(),16)
        print(math.log(h,2))
        while(h!=0):
            i=h%N
            h//=N
            if(out[i]!=1 or out[i]!=-1):
                out[i]=random.choice([-1,1])
                count+=1
            if(count==kappa):
                #out_poly=Poly([i for i in out])
                return out
        seed+=1


def H_non(input_bytes: bytes, output_length: int) -> bytes:
    hash_object = hashlib.sha256(input_bytes)

    hash_bytes = hash_object.digest()

    if output_length < len(hash_bytes):
        return hash_bytes[:output_length]
    # 如果需要的长度大于哈希结果的长度，就复制哈希结果直到达到需要的长度
    else:
        return (hash_bytes * (output_length // len(hash_bytes) + 1))[:output_length]

if __name__=="__main__":
    a=b'0000000000001111111111'
    b=b'0000000000001111111111'
    c=H_non(a,l)
    d=H_non(b,l)
    print(c,d)
