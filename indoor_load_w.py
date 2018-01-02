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
a_s = 0.7  # 外表面日射吸收率

# 1.1 壁体
# 透光面  1 窗 - (材料，朝向，面积，透光面积，透光率，吸收日射取得率, 贯流)
face_t = [[["6mm"], 45, 28, 24, 0.79, 0.04, 6.4]]
face_t_n = len(face_t)
# 不透光面  1 外壁  2 内壁  3 床  4 天井 - (类型，材料，厚度，朝向，面积，网格划分数)
face = [[1, ["concrete", "rock_wool", "air", "alum"], [0.150, 0.050, 0, 0.002], 45, 22.4, [7, 2, 1, 1]]]
face.append([2, ["concrete"], [0.120], 0, 100.8, [6]])
face.append([3, ["carpet", "concrete", "air", "stonebodo"], [0.015, 0.150, 0, 0.012], 0, 98, [1, 7, 1, 1]])
face.append([4, ["stonebodo", "air", "concrete", "carpet"], [0.012, 0, 0.150, 0.015], 0, 98, [1, 1, 7, 1]])
face_n = len(face)

# 预处理-计算(UX, FI, FO, ARM, ANF, SDT, AR, Sn)
# 定常
FI = []
FO = []
face_ul = []
face_ur = []
face_ux = []
A = []
for i in range(face_t_n):
    # FI, FO
    FI.append(1 - face_t[i][6] / alpha_i)
    FO.append(face_t[i][6] / alpha_i)
    # 面积
    A.append(face_t[i][2])
# 非定常
for i in range(face_n):
    # ul, ur, ux
    if face[i][0] == 1:
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
for i in range(face_t_n):
    Sn.append(0.7 * face_t[i][2] / Arm)
for i in range(face_n):
    if face[i][0] == 3:
        Sn.append(0.3 + 0.7 * face[i][4] / Arm)
    else:
        Sn.append(0.7 * face[i][4] / Arm)

# 1.2 内扰(室容积，热容量，人员，照明，设备，隙风)
# 室容积 热容量
VOL = 353
CPF = 3500
RMDT = (1.005 * 1.2 * VOL + CPF * 1000) / dt
# 人员
N_H = 16  # 在室人数
H_T = 119  # 全放热量
H_S24 = 62  # 24度的显热量
H_d = 4  # 勾配
# 照明
W_LI = 2900
# 设备
W_AS = 500
W_AL = 0
# 间隙风 [kg/s]
n_air = 0.2  # 换气回数
Go = 1.2 * n_air * VOL / 3600

# 2. 边界条件 (一年份)
# 2.1 气象数据 (外气温度，湿度，直达日射，太阳辐射，长波放射)
weather_data = readcsv.weather()
RN = weather_data["RN"]
x = weather_data["x"]
outdoor_temp = weather_data["outdoor_temp"]

# 2.2 日射量，日射取得热
# 窗
face_t_gt = []
face_t_ga = []
for i in range(face_t_n):
    Q_GT, Q_GA, Q_GO = load_window.load_window(26, face_t[i][1], 90, face_t[i][2], face_t[i][2] / face_t[i][3],
                                               face_t[i][4], face_t[i][5], face_t[i][6])
    face_t_gt.append(list(Q_GT))
    face_t_ga.append(list(Q_GA))
Q_gt = np.sum(np.array(face_t_gt), axis=0)
# 墙
out_wall = [face[i] for i in range(face_n) if face[i][0] == 1]
face_wall_n = len(out_wall)
in_wall = [face[i] for i in range(face_n) if face[i][0] == 2]
face_in_wall_n = len(in_wall)
up_down_wall = [face[i] for i in range(face_n) if face[i][0] == 3 or face[i][0] == 4]
face_up_down_wall_n = len(up_down_wall)
face_iw = []
for i in range(face_n):
    I_d, I_s, I_r, cos_theta, _Fs, _w = solar_radiation.solar_radiation_for_load_window(face[i][3])
    I_w = I_d + I_s + I_r
    face_iw.append(list(I_w))

# 2.3 相当外气温度
# 窗
face_t_te = []
for i in range(face_t_n):
    te = np.divide(face_t_ga[i], face_t[i][2] * face_t[i][6]) - (epsilon * Fs * RN) / alpha_o + outdoor_temp
    face_t_te.append(list(te))
# 外墙 
face_wall_te = []
for i in range(face_wall_n):
    te = (np.multiply(a_s, face_iw[i]) - epsilon * Fs * RN) / alpha_o + outdoor_temp
    face_wall_te.append(list(te))

# 2.4 日程表
sche = [0] * 8 + [1] * 12 + [0] * 4  # 9-18
sche_year = sche * 365

# 3 初始条件的设定
T_R = 5
face_tn = []
for i in range(face_n):
    tn = np.ones(np.array(face_ul[i]).shape) * T_R
    face_tn.append(tn)

# 输出
t_r_output = []
t_r_delta_output = []
q0 = []
output = []

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
    CF = [0] * face_t_n
    for i in range(face_n):
        cf = np.dot(face_ux[i][0], face_tn[i])
        CF.append(cf)
    # RSn
    RS = [Sn[i] * (Q_gt[step] + HG_r) / A[i] for i in range(face_t_n + face_n)]

    # AFT
    TE = []
    for i in range(face_t_n):
        TE.append(face_t_te[i][step])
    for i in range(face_wall_n):
        TE.append(face_wall_te[i][step])
    for i in range(face_in_wall_n):
        TE.append(0.7 * T_R + 0.3 * outdoor_temp[step])
    for i in range(face_up_down_wall_n):
        TE.append(T_R)
    AFT = np.multiply(A, (np.multiply(FO, TE) + np.multiply(FI, np.divide(RS, alpha_i)) + CF))
    AFT = np.sum(AFT)

    # CA
    CA = Arm * alpha_i * kc * AFT / SDT

    # BRM
    BRM = RMDT + AR + 1005 * Go
    BRC = RMDT * T_R + CA + 1005 * Go * outdoor_temp[step] + HG_c

    # T_R
    T_R_temp = BRC / BRM
    delta_T_R = T_R_temp - T_R
    T_R = T_R_temp
    t_r_output.append(T_R)
    t_r_delta_output.append(delta_T_R)
    # print(outdoor_temp[step], T_R)

    # 后处理
    # T_mrt
    T_mrt = (kc * ANF * T_R + AFT) / SDT

    # Tn
    T_sn = []
    for i in range(face_n):
        face_tn[i][0] += face_ul[i][0] * T_R
        face_tn[i][-1] += face_ur[i][-1] * TE[i]
        face_tn[i] = np.dot(face_ux[i], face_tn[i])
        T_sn.append(face_tn[i][0])
    q0.append(list(alpha_i * (T_R - T_sn)))

    if 1:#step > 4801 and step < 4825:
        output.append(outdoor_temp[step])
        output.append(T_R)
        output.append(T_mrt)
        output.extend(T_sn)
        output.extend(TE)
        output.extend(q0[step])
        output.append(RMDT * delta_T_R)
        output.append(CA-AR*T_R)
        output.append(1005 * Go * (outdoor_temp[step] - T_R))
        output.append(HG_c)
        output.append(Q_gt[step])
        output.append(HG_r)

#output = np.array(output).reshape(-1,22)
#print(output)
#np.savetxt('result_w.csv', output, delimiter = ',', fmt="%.3f")

'''
plt.plot(outdoor_temp)
plt.plot(t_r_output)
plt.show()
'''







