# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import solar_radiation

## 计算日照得热(对某扇窗而言)
# 输入 窗户朝向 尺寸 材质(默认) 室内温度
# 读取 外气温度 直达日射 扩散日射 反射日射 夜间放射
# 输出 透过 吸收 贯流 三种热取得

def load_window(indoor_temp, w_alpha, Ago, k=0.85, tau=0.48, Bn=0.12, K=4):
    # 输入室内温度
    #indoor_temp = 26
    # 窗户尺寸
    #Ago = 3.6
    Ags = k * Ago  # 窗框
    # 窗户材质 6mm吸热 + 6mm透明
    #tau = 0.48  # 透过
    #Bn = 0.12
    #K = 4.0
    # 直达日射 扩散日射 反射日射 夜间放射
    [I_D, I_s, I_r, cos_theta, Fs, weather_data] = solar_radiation.solar_radiation(w_alpha)
    outdoor_temp = weather_data["outdoor_temp"]
    RN = weather_data["RN"]
    '''
    # 测试用数据
    RN[4862] = 26
    outdoor_temp[4862] = 33.5
    '''
    # 计算热取得
    I_d = I_s + I_r
    CId = 3.4167 * cos_theta - 4.3890 * np.power(cos_theta, 2) + 2.4948 * np.power(cos_theta, 3) - 0.5224 * np.power(cos_theta, 4)
    Cd = 0.91
    Fsdw = 0
    epsilon = 0.9
    alpha_o = 23
    Q_GT = Ags * tau * ((1-Fsdw) * CId * I_D + 0.91 * I_d)
    Q_GA = Ags * Bn * ((1-Fsdw) * CId * I_D + 0.91 * I_d)
    Q_GO = Ago * K * (outdoor_temp - epsilon * Fs * RN / alpha_o - indoor_temp)
    return [Q_GT, Q_GA, Q_GO]

