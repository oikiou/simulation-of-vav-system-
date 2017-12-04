# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import readcsv
import solar_radiation

## 计算日照得热(对一面窗而言)
# 输入 窗户朝向 尺寸 材质
# 读取 外气温度 直达日射 天空日射 夜间放射 太阳高度 方位
# 输出 透过 吸收 贯流 三种热取得

# 输入窗户尺寸
Ago = 3.6
Ags = 0.85*Ago
# 窗户材质 6mm吸热 + 6mm透明
tau = 0.48
rho = 0.08
a = 0.44
Bn = 0.12
# 直达日射 水平面天空日射 夜间放射
[I_d, I_s, I_r] = solar_radiation.solar_radiation()
[outdoor_temp, _, I_dn, I_sky, RN, __, P] = readcsv.weather()

# 计算热取得
