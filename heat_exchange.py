# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

### 热通过有效度
## 通过额定参数 计算盘管热通过有效度
# 输入 定格 流体1入口温度 流量 流体2入口温度 流量 加热能力
# 输出 热通过有效度
def hx_e_e(t1, t2, f1, f2, power, l1, l2):
    dic = {"water":[4186, 1000],
           "air":[1005, 1.2]}  # 比热 密度
    c1 = dic[l1][0]  # [J/kg.K]
    c2 = dic[l2][0]
    rho1 = dic[l1][1]  # [kg/m3]
    rho2 = dic[l2][1]
    G1 = rho1 * f1  # [kg/s]
    G2 = rho2 * f2
    cG1 = c1 * G1  # [W/K]
    cG2 = c2 * G2
    epsilon = power / np.min((cG1, cG2)) / np.abs(t1 - t2)
    return epsilon

# 测试数据
t1 = 60  # [C]
t2 = 22
f1 = 0.004/60  # [m3/s]
f2 = 340/3600  # [m3/s]
power = 3200  # [w]
print(hx_e_e(t1,t2,f1,f2,power, l1="water", l2="air"))

## 盘管实际出口温度计算
# 输入 流体1入口温度 流量 比热 流体2入口温度 流量 比热 热通过有效度
# 输出 流体1出口温度 流体2出口温度
# hx_e_t


### 热贯流率和盘管面积 对数温差
## 通过定额参数 计算需要的换热面积
# 输入
# 输出 需要的换热面积






