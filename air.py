# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

## 湿空气线图的相关计算
# 绝对温度计算饱和水蒸气压[kPa]
def t2pws(t):
    return np.exp(-5800.2206*np.power(t,-1) + 1.3914993-0.048640239*t + 0.41764768*0.0001*np.power(t,2)
                  - 0.14452093*0.0000001*np.power(t,3) + 6.5459673*np.log(t))/1000

# 水蒸气分压力求露点温度[K]
def pw2t(pw):
    y = np.log(1000 * pw)
    return -77.199 + 13.198*y -0.63772*np.power(y,2) + 0.71098*np.power(y,3)

# 水蒸气分压力计算绝对湿度[kg/kg]
def pw2x(pw,p=101.325):
    return 0.62198*pw/(p-pw)

# 绝对湿度计算水蒸气分压力[kPa]
def x2pw(x,p=101.325):
    return x*p/(x+0.62198)

# 温度和水蒸气分压力求相对湿度
def t_pw2phi(t,pw):
    return pw*100/t2pws(t)

# 温度和相对湿度求水蒸气分压力
def t_phi2pw(t,phi):
    return phi/100*t2pws(t)

# 相对湿度和水蒸气分压力求温度
def phi_pw2t(phi,pw):
    return pw2t(100/phi*pw)

# 水蒸气分压和饱和水蒸气分压计算相对湿度[%]
def pw_pws2phi(pw,pws):
    return pw/pws*100

# 温度和绝对湿度计算焓值[J/kg]
def t_x2h(t,x):
    return 1005*t+(1846*t+2501000)*x

# 绝对湿度和焓值计算干球温度
def x_h2t(x,h):
    return (h-2501000*x)/(1005+1846*x)

# 干球温度和焓值计算绝对湿度
def t_h2x(t,h):
    return (h-1005*t)/(1846*t+2501000)

# 干球温度和绝对湿度求湿球温度
