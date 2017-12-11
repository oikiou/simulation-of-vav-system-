# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

# 读取气象参数
def weather():
    data = np.array(np.loadtxt(open(r"東京気象データ.csv","r"),delimiter=",",skiprows=2))
    weather_data ={"outdoor_temp":data[:,1],
                   "x":data[:,2],
                   "I_dn":data[:,3],
                   "I_sky":data[:,4],
                   "RN":data[:,5],
                   "CC":data[:,6],
                   "P":data[:,9]}

    return weather_data

def weather_m():
    data = np.array(np.loadtxt(open(r"TOKYO_epw_m.csv", "r"), delimiter=",", skiprows=1))
    outdoor_temp = data[:,0]
    CC = data[:,16]
    P = data[:,3]
    Br = 0.51 + 0.000209 * np.sqrt(P)
    R_sky = np.multiply((np.multiply((1 - 0.062 * CC), Br) + 0.062 * CC), (5.67 * 0.00000001 * np.power((outdoor_temp + 273.15), 4)))
    RN = (5.67 * 0.00000001 * np.power((outdoor_temp + 273.15), 4)) - R_sky
    weather_data = {"outdoor_temp":data[:,0],
                    "phi":data[:,2],
                    "I_dn":data[:,8],
                    "I_sky":data[:,9],
                    "RN":RN
                    }
    return weather_data

