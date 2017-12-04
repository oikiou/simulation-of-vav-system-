# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

# 读取气象参数
def weather():
    data = np.array(np.loadtxt(open(r"東京気象データ.csv","r"),delimiter=",",skiprows=2))
    outdoor_temp = data[:,1]
    x = data[:,2]
    I_dn = data[:,3]
    I_sky = data[:,4]
    RN = data[:,5]
    CC = data[:,6]
    P = data[:,9]

    return [outdoor_temp, x, I_dn, I_sky, RN, CC, P]
