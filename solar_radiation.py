# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import sun
import readcsv
from my_math import *

## 计算日射量(对某一个面而言)
# 输入 朝向
# 读取 直达日射 天空日射 太阳高度 方位
# 输出 直达 扩散 反射 三个日射量

def solar_radiation(w_alpha=112.5, w_beta=90):
    # 朝向
    # w_alpha = 112.5  # 正南夹角
    # w_beta = 90  # 地面夹角
    sin_w_beta = np.sin(deg_to_rad(w_beta))
    cos_w_beta = np.cos(deg_to_rad(w_beta))
    sin_w_alpha = np.sin(deg_to_rad(w_alpha))
    cos_w_alpha = np.cos(deg_to_rad(w_alpha))
    # 直达日射 水平面天空日射 夜间放射
    [_temp, _x, I_dn, I_sky, _RN, _cc, _P] = readcsv.weather()
    rho = 0.2  # 地面反射
    # 太阳高度 方位
    h, A = sun.h_A()  # 4862
    sin_h = np.sin(deg_to_rad(h))
    cos_h = np.cos(deg_to_rad(h))
    sin_A = np.sin(deg_to_rad(A))
    cos_A = np.cos(deg_to_rad(A))
    '''
    # 测试用数据
    I_dn[4862] = 739
    I_sky[4862] = 116
    '''
    # 计算入射角
    sh = np.sin(deg_to_rad(h))
    sw = np.multiply(cos_h, sin_A)
    ss = np.multiply(cos_h, cos_A)
    wz = np.cos(deg_to_rad(w_beta))
    ww = np.multiply(sin_w_beta, sin_w_alpha)
    ws = np.multiply(sin_w_beta, cos_w_alpha)
    cos_theta = np.multiply(sh,wz) + np.multiply(sw,ww) + np.multiply(ss,ws)
    # 计算日射量
    theta = rad_to_deg(np.arccos(cos_theta))
    I_d = np.multiply(I_dn, cos_theta)
    Fs = 0.5 * (1 + cos_w_beta)
    I_s = Fs * I_sky
    Fg = 1 - Fs
    I_hol = np.multiply(I_dn, sin_h) + I_sky
    I_r = rho * Fg * I_hol
    #  I = I_d + I_s + I_r
    return [I_d, I_s, I_r]


