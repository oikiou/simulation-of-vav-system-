# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

## 计算全年的太阳方位角和高度角
def sun_h_A():
    # 地理条件设定
    phi = 35.68  # 纬度
    L = 139.77  # 经度
    sin_phi = np.sin(phi*np.pi/180)
    cos_phi = np.cos(phi*np.pi/180)

    # 大气圈外日射量 *
    i0 = [1370*(1+0.033*np.cos(2*np.pi*i/365)) for i in range(365)]

    # 计算均时差 真太阳时 时角
    B = [360*(i/24-81)/365 for i in range(8760)]
    E = [1/60*(9.87*np.sin(2*b*np.pi/180)-7.53*np.cos(b*np.pi/180)-1.5*np.sin(b*np.pi/180)) for b in B]
    tas = [(i%24+1)+E[i]+(L-135)/15 for i in range(8760)]
    omega = [(t-12)*15 for t in tas]

    # 计算太阳赤纬
    sin_delta = [0.397949*np.sin(b*np.pi/180) for b in B]
    cos_delta = [np.cos(np.arcsin(s)) for s in sin_delta]

    # 计算太阳高度角
    sin_h = [sin_phi*sin_delta[i] + cos_phi*cos_delta[i]*np.cos(omega[i]*np.pi/180) for i in range(8760)]
    h = np.arcsin(sin_h)
    cos_h = np.cos(h)

    # 计算太阳方位角
    cos_A = [(sin_h[i]*sin_phi-sin_delta[i])/(cos_h[i]*cos_phi) for i in range(8760)]
    A = [omega[i]/abs(omega[i])*np.arccos(cos_A[i]) for i in range(8760)]

    # 输出
    return [h,A]

