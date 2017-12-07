# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import time

def diff_m(material, d, m, dt, t0, t1, t2, time, method="forward"):
    # material 材料 wood concrete rock_wool中选，列表
    # d 厚度，列表 [m]
    # m 每种材质的分隔数量，列表
    # dt 时间间隔 [s]
    # t0 初始温度
    # t1 边界1温度
    # t2 边界2温度
    # time 计算的时长
    # method 方法，前进，后退选1个

    # 输入检测
    if len(material) != len(d) or len(d) != len(m):
        return None

    # 材质库
    material_lambda = {"wood": 0.19,
                       "concrete": 1.4,
                       "rock_wool": 0.042}
    material_c_rho = {"wood": 716000,
                      "concrete": 1934000,
                      "rock_wool": 84000}

    # 默认参数
    alpha0 = 9.3  # 内表面换热系数
    alpham = 9.3  # 外表面换热系数

    # 网格尺寸，物性参数
    M = sum(m)  # 网格总数
    dx = [0]
    dx_c_rho = [0]
    dx_lambda = [alpha0]
    for i in range(len(m)):
        for j in range(m[i]):
            dx.append(d[i] / m[i])
            dx_lambda.append(material_lambda[material[i]])
            dx_c_rho.append(material_c_rho[material[i]])
    dx.append(0)
    dx_lambda.append(alpham)
    dx_c_rho.append(0)
    dx = np.array(dx)
    dx_lambda = np.array(dx_lambda)
    dx_c_rho = np.array(dx_c_rho)

    # 计算R值
    dx1 = dx
    dx1[0] = dx1[-1] = 1
    r = np.divide(dx1, dx_lambda)

    # 计算CAP值
    cap = np.multiply(dx_c_rho, dx)

    # 安定条件检测
    dt_check = [0.5 * (cap[i] + cap[i + 1]) / (1 / r[i] + 1 / r[i + 1]) for i in range(M + 1)]
    if min(dt_check) < dt and method == "forward" :
        msg = "delta_t check failed, decrease the delta_t"
        return msg,msg,msg

    # ul和ur的计算
    ul = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i] for i in range(M + 1)]
    ur = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i + 1] for i in range(M + 1)]
    um = np.multiply(np.add(ul, ur), -1) + 1

    # 温度计算
    t_out = []
    t_old_m = [t0] * (M + 1)  # 初始条件
    if method == "forward":
        # 前进差分
        for i in range(int(time / dt)):
            t_old_l = [t1] + list(t_old_m[:-1])  # 边界条件
            t_old_r = list(t_old_m[1:]) + [t2]  # 边界条件
            t_new = np.multiply(ul, t_old_l) + np.multiply(um, t_old_m) + np.multiply(ur, t_old_r)
            t_out.extend(list(t_new))
            t_old_m = t_new
    elif method == "backward":
        # 后退差分
        # 计算逆矩阵
        u = np.zeros((M+1, M+1))
        for i in range(M):
            u[i][i] = 1 + ul[i] + ur[i]
            u[i + 1][i] = -ul[i+1]
            u[i][i + 1] = -ur[i]
        u[-1][-1] = 1 + ul[-1] + ur[-1]
        u = np.matrix(u)
        ux = u.I
        # 计算温度
        t_old_m[0] += ul[0] * t1  # 边界条件
        t_old_m[-1] += ur[-1] * t2  # 边界条件
        t_old_m = np.array(t_old_m).reshape(5, 1)
        for i in range(int(time / dt)):
            t_new = np.dot(ux, t_old_m)
            t_out.append(t_new.copy())
            t_old_m = t_new
            t_old_m[0] += ul[0] * t1  # 边界条件
            t_old_m[-1] += ur[-1] * t2  # 边界条件
    # 整理格式
    t_out = np.array(t_out)
    t_out = t_out.reshape((-1, M + 1))

    # 热流计算
    q0 = [alpha0 * (t1 - t_out[i][0]) for i in range(int(time/dt))]
    qm = [alpham * (t2 - t_out[i][-1]) for i in range(int(time/dt))]

    # 返回值
    return t_out, q0, qm

    # 两边不是温度 是热流 或者得热


# 测试数据
material = ["wood", "concrete", "rock_wool"]
d = [0.025, 0.12, 0.05]  # 厚度[m]
m = [1, 2, 1]  # 网格划分数
dt = 60  # [s]
t0 = 10
t1 = 20
t2 = 10
time_length = 3600*8760

## 前进和后退的比较
a1 = time.time()
t,q0,qm = diff_m(material, d, m, dt, t0, t1, t2, time_length, method="forward")
b1 = time.time()
'''
print(t)
print(q0)
print(qm)
'''
print(b1-a1)

c1 = time.time()
t,q0,qm = diff_m(material, d, m, dt, t0, t1, t2, time_length, method="backward")
d1 = time.time()
'''
print(t)
print(q0)
print(qm)
'''
print(d1-c1)





