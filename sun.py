# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from my_math import *

## 计算全年的太阳方位角和高度角
def h_A(phi=35.68,L=139.77):
    # 地理条件设定
    sin_phi = np.sin(deg_to_rad(phi))
    cos_phi = np.cos(deg_to_rad(phi))

    # 大气圈外日射量 *
    i0 = [1370*(1+0.033*np.cos(2*np.pi*i/365)) for i in range(365)]

    # 计算均时差 真太阳时 时角
    B = [360*(i/24-81)/365 for i in range(8760)]
    E = [1/60*(9.87*np.sin(2*deg_to_rad(b))-7.53*np.cos(deg_to_rad(b))-1.5*np.sin(deg_to_rad(b))) for b in B]
    tas = [(i%24+1)+E[i]+(L-135)/15 for i in range(8760)]
    omega = [(t-12)*15 for t in tas]

    # 计算太阳赤纬
    sin_delta = [0.397949*np.sin(deg_to_rad(b)) for b in B]
    cos_delta = [np.cos(np.arcsin(s)) for s in sin_delta]

    # 计算太阳高度角
    sin_h = [sin_phi*sin_delta[i] + cos_phi*cos_delta[i]*np.cos(deg_to_rad(omega[i])) for i in range(8760)]
    h = rad_to_deg(np.arcsin(sin_h))
    cos_h = np.cos(np.arcsin(sin_h))

    # 计算太阳方位角
    cos_A = [(sin_h[i]*sin_phi-sin_delta[i])/(cos_h[i]*cos_phi) for i in range(8760)]
    A = np.array([rad_to_deg(omega[i]/abs(omega[i])*np.arccos(cos_A[i])) for i in range(8760)])

    # 输出
    return [h,A]

