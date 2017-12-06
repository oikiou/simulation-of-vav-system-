# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

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
    if len(material) == len(d) == len(m):
        if method == "forward":
            diff_forward(material,d,m,dt,t0,t1,t2,time)
        elif method == "backward":
            diff_backward(material,d,m,dt,t0,t1,t2,time)
    else:
        return None

## 前进差分
def diff_forward(material,d,m,dt,t0,t1,t2,time):
    material_lambda = {"wood": 0.19,
                       "concrete": 1.4,
                       "rock_wool": 0.042}
    material_c_rho = {"wood": 716000,
                      "concrete": 1934000,
                      "rock_wool": 84000}

    alpha0 = 9.3  # 表面换热系数
    M = sum(m)  # 总的网格数

    # 网格尺寸，物性参数
    dx = [0]
    dx_c_rho = [0]
    dx_lambda = [alpha0]
    for i in range(len(m)):
        for j in range(m[i]):
            dx.append(d[i] / m[i])
            dx_lambda.append(material_lambda[material[i]])
            dx_c_rho.append(material_c_rho[material[i]])
    dx.append(0)
    dx_lambda.append(alpha0)
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
    if min(dt_check) < dt:
        return "delta_t check failed, decrease the delta_t"

    # ul和ur的计算
    ul = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i] for i in range(M + 1)]
    ur = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i + 1] for i in range(M + 1)]
    um = np.multiply(np.add(ul, ur), -1) + 1

    # 温度计算
    t_out = []
    t_old_m = [t0] * (M + 1)
    for i in range(int(time / dt)):
        t_old_l = [t1] + list(t_old_m[:-1])
        t_old_r = list(t_old_m[1:]) + [t2]
        t_new = np.multiply(ul, t_old_l) + np.multiply(um, t_old_m) + np.multiply(ur, t_old_r)
        t_out.extend(list(t_new))
        t_old_m = t_new
    t_out = np.array(t_out)
    t_out = t_out.reshape((-1, M + 1))
    return t_out

    # 热流计算
    # 明天做

    # 两边不是温度 是热流 或者得热
    # to be continue

# 测试数据
material = ["wood", "concrete", "rock_wool"]
d = [0.025, 0.12, 0.05]  # 厚度[m]
m = [1, 2, 1]  # 网格划分数
dt = 60  # [s]
t0 = 10
t1 = 20
t2 = 10
time = 1800
t = diff_forward(material, d, m, dt, t0, t1, t2, time)
print(t)


## 后退差分
def diff_backward(material,d,m,dt,t0,t1,t2,time):
    # 这个也明天做
    pass


## 前进和后退的比较
# to be continue

