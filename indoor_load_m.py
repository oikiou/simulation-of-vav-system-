# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import difference_methods
import readcsv
import air
import solar_radiation
import load_window
import matplotlib.pyplot as plt

## 热负荷计算programme

# 1. input
# 时间间隔
dt = 3600
# 表面换热系数
alpha_i = 9.3
alpha_o = 23
# 对流和辐射的比例
kc = 0.45
kr = 0.55
# 长波辐射率
epsilon = 0.9
# 综合外壁特性
Fs = 0.5  # 天空的水平面和前直面的比例
rho_g = 0.2  # 地面反射率
a_s = 0.8  # 外表面日射吸收率

# 1.1 壁体
'''
# 透光面  1 窗 - (材料，朝向，面积，透光面积，透光率，吸收日射取得率, 贯流)
face_t = [[]]
face_t_n = len(face_t)
'''
# 不透光面  1 外壁  2 内壁  3 床  4 天井 - (类型，材料，厚度，朝向，面积，网格划分数)
face = [[1, ["wood_m"], [0.2], -90, 16, [10]]]
face.append([1, ["wood_m"], [0.2], 0, 16, [10]])
face.append([1, ["wood_m"], [0.2], 90, 16, [10]])
face.append([1, ["wood_m"], [0.2], 180, 16, [10]])
face.append([3, ["wood_m"], [0.2], 0, 16, [10]])
face.append([4, ["wood_m"], [0.2], 0, 16, [10]])
face_n = len(face)

# 预处理-计算(UX, FI, FO, ARM, ANF, SDT, AR, Sn)
# 定常
FI = []
FO = []
face_ul = []
face_ur = []
face_ux = []
A = []
'''
for i in range(face_t_n):
    # FI, FO
    FI.append(1 - face_t[i][6] / alpha_i)
    FO.append(face_t[i][6] / alpha_i)
    # 面积
    A.append(face_t[i][2])
'''
# 非定常
for i in range(face_n):
    # ul, ur, ux
    if face[i][0] == 1 or face[i][0] == 4 or face[i][0] == 3:
        ul, ur, ux = difference_methods.diff_ux(face[i][1], face[i][2], face[i][5], dt, alpha_i, alpha_o)
    else:
        ul, ur, ux = difference_methods.diff_ux(face[i][1], face[i][2], face[i][5], dt, alpha_i, alpha_i)
    face_ul.append(ul)
    face_ur.append(ur)
    face_ux.append(ux)
    # FI, FO
    FI.append(ux[0][0] * ul[0])
    FO.append(ux[0][-1] * ur[-1])
    # 面积
    A.append(face[i][4])
# ARM, ANF, SDT, AR, Sn
Arm = sum(A)
ANF = np.dot(A, FI)
SDT = Arm - kr * ANF
AR = Arm * alpha_i * kc * (1 - kc * ANF / SDT)
Sn = []
'''
for i in range(face_t_n):
    Sn.append(0.7 * face_t[i][2] / Arm)
'''
for i in range(face_n):
    if face[i][0] == 3:
        Sn.append(0.3 + 0.7 * face[i][4] / Arm)
    else:
        Sn.append(0.7 * face[i][4] / Arm)

# 1.2 内扰(室容积，热容量，人员，照明，设备，隙风)
# 室容积 热容量
VOL = 64
CPF = 640
RMDT = (1.005 * 1.2 * VOL + CPF * 1000) / dt
# 人员
N_H = 0  # 在室人数
H_T = 119  # 全放热量
H_S24 = 62  # 24度的显热量
H_d = 4  # 勾配
# 照明
W_LI = 0
# 设备
W_AS = 0
W_AL = 0
# 间隙风 [kg/s]
n_air = 0  # 换气回数
Go = 1.2 * n_air * VOL / 3600

# 2. 边界条件 (一年份)
# 2.1 气象数据 (外气温度，湿度，直达日射，太阳辐射，长波放射)
weather_data = readcsv.weather_m()
RN = weather_data["RN"]
outdoor_temp = weather_data["outdoor_temp"]

# 2.2 日射量，日射取得热
'''
# 窗
face_t_gt = []
face_t_ga = []
for i in range(face_t_n):
    Q_GT, Q_GA, Q_GO = load_window.load_window(26, face_t[i][1], face_t[i][2], face_t[i][2] / face_t[i][3],
                                               face_t[i][4], face_t[i][5], face_t[i][6])
    face_t_gt.append(list(Q_GT))
    face_t_ga.append(list(Q_GA))
Q_gt = np.sum(np.array(face_t_gt), axis=0)
'''
# 墙
out_wall = [face[i] for i in range(face_n) if face[i][0] == 1]
face_wall_n = len(out_wall)

in_wall = [face[i] for i in range(face_n) if face[i][0] == 2]
face_in_wall_n = len(in_wall)

up_wall = [face[i] for i in range(face_n) if face[i][0] == 4]
face_up_wall_n = len(up_wall)

down_wall = [face[i] for i in range(face_n) if face[i][0] == 3]
face_down_wall_n = len(down_wall)

face_wall_iw = []
for i in range(face_wall_n):
    I_d, I_s, I_r, cos_theta, _Fs, _w = solar_radiation.solar_radiation_for_load_window(face[i][3], 90)
    I_w = I_d + I_s + I_r
    face_wall_iw.append(list(I_w))

face_up_wall_iw = []
for i in range(face_up_wall_n):
    I_d, I_s, I_r, cos_theta, _Fs, _w = solar_radiation.solar_radiation_for_load_window(face[i][3], 0)
    I_w = I_d + I_s + I_r
    face_up_wall_iw.append(list(I_w))

# 2.3 相当外气温度
'''
# 窗
face_t_te = []
for i in range(face_t_n):
    te = np.divide(face_t_ga[i], face_t[i][2] * face_t[i][6]) - (epsilon * Fs * RN) / alpha_o + outdoor_temp
    face_t_te.append(list(te))
'''
# 外墙
face_wall_te = []
for i in range(face_wall_n):
    te = (np.multiply(a_s, face_wall_iw[i]) - epsilon * Fs * RN) / alpha_o + outdoor_temp
    face_wall_te.append(list(te))
# 天井
face_up_wall_te = []
for i in range(face_up_wall_n):
    te = (np.multiply(a_s, face_up_wall_iw[i]) - epsilon * Fs * RN) / alpha_o + outdoor_temp
    face_up_wall_te.append(list(te))

# 2.4 日程表
sche = [0] * 8 + [1] * 12 + [0] * 4  # 9-18
sche_year = sche * 365

# 3 初始条件的设定
T_R = 10
face_tn = []
for i in range(face_n):
    tn = np.ones(np.array(face_ul[i]).shape) * T_R
    face_tn.append(tn)

# 输出
t_r_output = []

# 4 循环开始
for step in range(8760):
    # HG_c
    # 人体
    H_s = H_S24 - H_d * (T_R - 24)
    H_l = H_T - H_s
    Q_HS = N_H * H_s
    Q_HL = N_H * H_l
    # 室内发热对流成分
    HG_c = (0.5 * Q_HS + 0.6 * W_LI + 0.6 * W_AS) * sche_year[step]
    # 室内发热辐射成分
    HG_r = (0.5 * Q_HS + 0.4 * W_LI + 0.4 * W_AS) * sche_year[step]
    # 潜热
    HLG = (Q_HL + W_AL) * sche_year[step]

    # CFn
    CF = []
    for i in range(face_n):
        cf = np.dot(face_ux[i][0], face_tn[i])
        CF.append(cf)

    '''
    # RSn
    RS = [Sn[i] * (Q_gt[step] + HG_r) / A[i] for i in range(face_t_n + face_n)]
    '''

    # AFT
    TE = []
    '''
    for i in range(face_t_n):
        TE.append(face_t_te[i][step])
    '''
    for i in range(face_wall_n):
        TE.append(face_wall_te[i][step])
    for i in range(face_up_wall_n):
        TE.append(face_up_wall_te[i][step])
    for i in range(face_down_wall_n):
        TE.append(outdoor_temp[step])

    AFT = np.multiply(A, (np.multiply(FO, TE) + CF))
    AFT = np.sum(AFT)

    # CA
    CA = Arm * alpha_i * kc * AFT / SDT

    # BRM
    BRM = RMDT + AR + 1005 * Go
    BRC = RMDT * T_R + CA + 1005 * Go * outdoor_temp[step] + HG_c

    # T_R
    T_R = BRC / BRM
    t_r_output.append(T_R)
    #print(outdoor_temp[step], T_R)

    # 后处理
    # T_mrt
    T_mrt = (kc * ANF * T_R + AFT) / SDT

    # Tn
    for i in range(4):
        face_tn[i][0] += face_ul[i][0] * T_R
        face_tn[i][-1] += face_ur[i][-1] * TE[i]
        face_tn[i] = np.dot(face_ux[i], face_tn[i])


plt.plot(outdoor_temp)
plt.plot(t_r_output)
plt.show()







