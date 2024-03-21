from musigl import *

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
        off,st = sign_off(sk)
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