from musigl import *
import time
from utils import *

# 创建n个参与者
def create_participants():
    participants = []
    for _ in range(n):
        pk, sk = Gen()
        participant_info = [pk, sk] 
        participants.append(participant_info)
    return participants

def aggregate_pub_keys(participants):
    pub_keys = [info[0] for info in participants]  # 提取每个参与者的公钥
    agg_pub_key = aggregate_public_keys(pub_keys)  # 使用你的聚合函数
    return agg_pub_key

# 签名阶段
def sign_total(participants, message):
    pub_keys = [info[0] for info in participants]  # 提取每个参与者的公钥
    msgs= []
    # 每个参与者计算自己的签名份额，并追加到各自的信息列表中
    for info in participants:
        pk, sk = info[:2]  # 提取公钥和私钥
        off,st = sign_off(sk,pk)
        #info.append(off)
        info.append(st)
        msgs.append(off)

    on_list=[]
    for info in participants:
        on=sign_online(info[2],info[1],msgs,message,pub_keys)
        on_list.append(on)
    sig=aggregate(on_list)
    return sig



def run_protocol(message):
    # 步骤1: 创建参与者
    participants = create_participants()

    # 步骤2：聚合公钥
    agg_pub_key = aggregate_pub_keys(participants)

    # 步骤3: 签名消息
    agg_sigma = sign_total(participants, message)

    # 步骤4: 验证签名
    is_valid = verify_sig(agg_pub_key,agg_sigma, message)

    print(f"Signature is valid: {is_valid}")

# 模拟协议运行
if __name__ == "__main__":
    message = "This is a test message."
    run_protocol(message)
    
    # print("message: This is a test message")
    # print()
    # print("create",n,"participants…………  succussful")
    # print()
    # print("aggregate public keys now……")
    # print("before aggregate: ")
    # print("pk1: Polynomial([6.4220e+03, 3.7270e+03, 2.2890e+03, 9.9610e+03, 1.1544e+04,……])")
    # print("pk2: Polynomial([7.7100e+02, 4.9290e+03, 2.7150e+03, 3.9790e+03, 3.4060e+03,……])")
    # print("pk3: Polynomial([1.1202e+04, 7.8720e+03, 1.5020e+03, 6.8180e+03, 9.6480e+03,……])")
    # print("aggregate key: Polynomial([7.7090e+03, 9.8680e+03, 1.1079e+04, 5.0700e+03, 5.3630e+03,……])")
    # print("aggregate public keys successful")
    # print("time of aggregate public keys: 16.865s")
    # print()
    # print("signing message……")
    # print("signature: (Polynomial([5.5030e+03, 1.1140e+04, 3.1600e+02, 4.1300e+02, 1.4000e+03,……]), Polynomial([9.2250e+03, 7.2330e+03, 6.7760e+03, 2.2010e+03, 9.3670e+03,……]))")
    # print("signing successful")
    # print("time of signing: 314.277s")

    # print()
    # print("verify signature……")
    # print("Signature is valid: True")
    # print("time of verify signature: 1.859s")