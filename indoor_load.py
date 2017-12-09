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

# 1. 数据输入和计算准备
# 1.1 air.py的import和系数
# 表面热传达率
alpha_o = 23
alpha_i = 9.3
# 室内侧热传达对流辐射比
kc = 0.45
kr = 0.55
# 时间间隔
dt = 60

# 1.2 建筑尺寸和外壁材料输入
w_alpha = 45  # 朝向
rho_g = 0.2  # 地面反射率
a_s = 0.7  # 外表面日射吸收率
# 窗
A1 = 28  # 开口面积
K1 = 6.4  # 热贯流率
AG = 24  # 玻璃面积
tau_TN = 0.79  # 综合透过率
B_N = 0.04  # 吸收日射取得率
epsilon = 0.9  # 放射
# 外壁
A2 = 22.4
A2_material = ["concrete", "rock_wool", "air", "arumi"]
A2_d = [0.150, 0.050, 0, 0.2]
A2_m = [7, 2, 1, 1]
# 内壁
A3 = 100.8
A3_material = ["concrete"]
A3_d = [0.120]
A3_m = [6]
# 床
A4 = 98
A4_material = ["carpet", "concrete", "air", "stonebodo"]
A4_d = [0.015, 0.150, 0, 0.012]
A4_m = [1, 7, 1, 1]
# 天井
A5 = 98
A5_material = ["stonebodo", "air", "concrete", "carpet"]
A5_d = [0.012, 0, 0.150, 0.015]
A5_m = [1, 1, 7, 1]
# 室容积
VOL = 353
CPF = 3500

# 1.3 外表面的方向余弦(参考表6.5)

# 1.4 后退差分的ul, ur, ux计算 调用difference_method
A2_ul, A2_ur, A2_ux = difference_methods.diff_ux(A2_material, A2_d, A2_m, dt, alpha_i, alpha_o)
A3_ul, A3_ur, A3_ux = difference_methods.diff_ux(A3_material, A3_d, A3_m, dt, alpha_i, alpha_i)
A4_ul, A4_ur, A4_ux = difference_methods.diff_ux(A4_material, A4_d, A4_m, dt, alpha_i, alpha_i)
A5_ul, A5_ur, A5_ux = difference_methods.diff_ux(A5_material, A5_d, A5_m, dt, alpha_i, alpha_i)

# 1.5 FIn FOn
# 窗 定常
FI = [1 - K1/alpha_i]
FO = [K1/alpha_i]
# 外壁  # 内壁  # 床  # 天井 (特殊处理：天井看成是床的另一面？)
FI.extend([eval("A"+str(i+2)+"_ux[0][0] * A"+str(i+2)+"_ul[0]") for i in range(4)])
FO.extend([eval("A"+str(i+2)+"_ux[0][-1] * A"+str(i+2)+"_ur[-1]") for i in range(4)])

# 1.6 全室内表面积的计算 室内表面辐射吸收率的设定
A_list = [eval("A" + str(i+1)) for i in range(5)]
Arm = sum(A_list)
# S_Gn = S_Hn = S_Ln = S_An = S_n
S_list = [0.7 * A_list[i] / Arm for i in range(5)]
S_list[3] = 0.3 + 0.7 * A4 / Arm

# 1.7 求ANF SDT AR RMDT RMDTX
ANF = np.sum(np.multiply(A_list, FI))
SDT = Arm - kr * ANF
AR = Arm * alpha_i * kc * (1 - kc * ANF / SDT)
RMDT = (1005 * 1.2 * VOL + CPF) / dt
RMDTX = 1.2 * VOL / dt

# 2. 运转条件 气象条件的输入
# 2.1 输入 气象读入
# 换气回数
n_air = 0.2
# 室内发热
# 人体
N_H = 16  # 在室人数
H_T = 119  # 全放热量
H_S24 = 62  # 24度的显热量
H_d = 4  # 勾配
# 照明
W_LI = 2900
# 机器
W_AS = 500
W_AL = 0
# 空调设定
T_R_set = 26
phi_R_set = 60
# 气象数据
weather_data = readcsv.weather()
RN = weather_data["RN"]
outdoor_temp = weather_data["outdoor_temp"]

# 2.2 绝对湿度
x_R_set = air.pw2x(air.t_phi2pw(T_R_set+273.15, phi_R_set))

# 2.3 间隙风 [kg/s]
Go = 1.2 * n_air * VOL / 3600

# 2.4 室内发热
# 人体
H_s = H_S24 - H_d * (T_R_set - 24)
H_l = H_T - H_s
Q_HS = N_H * H_s
Q_HL = N_H * H_l
# 室内发热对流成分
HG_c = 0.5 * Q_HS + 0.6 * W_LI + 0.6 * W_AS
# 室内发热辐射成分
HG_r = 0.5 * Q_HS + 0.4 * W_LI + 0.4 * W_AS
# 潜热
HLG = Q_HL + W_AL

# 3. 初期値设定
# 差分法的初期値
T_R = T_R_set

# 4. 边界条件设定 (全年！)
# 4.3 日射量的计算
# 窗
[I_d, I_s, I_r, cos_theta, Fs] = solar_radiation.solar_radiation(w_alpha)
[Q_GT, Q_GA, Q_GO] = load_window.load_window(26, w_alpha, AG, k=0.85, tau=tau_TN, Bn=B_N, K=K1)
# Q_GO是没有用的，所以26度也无所谓
I_w = I_d + I_s + I_r

# 4.4 Ten的计算
T_e_1 = Q_GA / A1 / K1 - (epsilon * Fs * RN) / alpha_o + outdoor_temp
T_e_2 = (a_s * I_w - epsilon * Fs * RN) / alpha_o + outdoor_temp
T_e_3 = 0.7 * T_R + 0.3 * outdoor_temp






