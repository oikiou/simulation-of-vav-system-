# -*- coding: utf-8 -*-
import numpy as np
import readcsv

# 直达日射 水平面天空日射 夜间放射
weather_data = readcsv.weather()
I_dn = weather_data["I_dn"]
I_sky = weather_data["I_sky"]
rho_g = 0.2  # 地面反射

I_dn[4839] = 739
I_sky[4839] = 116

def d2r(d):
    return np.divide(np.multiply(3.14159265, d), 180)


def r2d(r):
    return np.divide(np.multiply(180, r), 3.14159265)


# 城市
class Cities(object):

    def __init__(self, name, latitude, longitude, time_zone):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.time_zone = time_zone

tokyo = Cities('tokyo', 35.68, 139.77, 9)
usco = Cities('USCO', 39.76, -104.86, -6)


# 太阳方位角和高度角的计算
# 输入为城市
# 输出为sun.h, sun.A
class Sun(object):
    """太阳日射，知道城市的经纬度和时区，自动生成全年或一段时间的太阳高度角和方位角"""
    hours_8760 = np.linspace(0, 8759, 8760)

    def __init__(self, city, hours=hours_8760):  # hours可以指定某一小时，或某一段时间，默认全年
        self.sin_latitude = np.sin(d2r(city.latitude))
        self.cos_latitude = np.cos(d2r(city.latitude))

        # 计算均时差 真太阳时 时角
        self.b = np.multiply(np.divide(hours, 24) - 81, 360/365)
        self.b_r = d2r(self.b)
        self.e = (9.87 * np.sin(2 * self.b_r) - 7.53 * np.cos(self.b_r) - 1.5 * np.sin(self.b_r)) / 60
        self.tas = np.mod(hours, 24) + self.e + (city.longitude - 15 * city.time_zone) / 15
        self.omega = np.multiply((self.tas - 12), 15)

        # 计算太阳赤纬
        self.sin_delta = np.multiply(np.sin(self.b_r), 0.397949)
        self.cos_delta = np.cos(np.arcsin(self.sin_delta))

        # 计算太阳高度角
        self.sin_h = np.multiply(self.sin_latitude, self.sin_delta) + \
                     np.multiply(np.multiply(self.cos_latitude, self.cos_delta), np.cos(d2r(self.omega)))
        self.h = r2d(np.arcsin(self.sin_h))
        self.cos_h = np.cos(np.arcsin(self.sin_h))

        # 计算太阳方位角
        self.cos_A = np.divide(np.multiply(self.sin_h, self.sin_latitude) - self.sin_delta, np.multiply(self.cos_h, self.cos_latitude))
        self.A = r2d(np.multiply(np.sign(self.omega), np.arccos(self.cos_A)))
        self.sin_A = np.sin(d2r(self.A))
        if isinstance(self.A, np.ndarray):
            self.h[self.h < 0] = 0
            self.A[self.h == 0] = 0


sun = Sun(tokyo)  # 对于一栋建筑而言，有且只有一个地理位置，故只有一个太阳高度和方位的list
# 类似于气象参数，I_DN I_SKY 一个项目只有一个
# print(sun.h, sun.A)


class Face(object):
    """外墙和外窗继承自face，有日照相关的函数"""

    def __init__(self, orientation, tilt):
        self.orientation = orientation
        self.tilt = tilt

    def solar_radiation(self):
        # 墙面的三角函数
        self.sin_orientation = np.sin(d2r(self.orientation))
        self.cos_orientation = np.cos(d2r(self.orientation))
        self.sin_tilt = np.sin(d2r(self.tilt))
        self.cos_tilt = np.cos(d2r(self.tilt))

        # 计算入射角
        self.sh = sun.sin_h
        self.sw = np.multiply(sun.cos_h, sun.sin_A)
        self.ss = np.multiply(sun.cos_h, sun.cos_A)

        self.wz = self.cos_tilt
        self.ww = np.multiply(self.sin_tilt, self.sin_orientation)
        self.ws = np.multiply(self.sin_tilt, self.cos_orientation)

        self.cos_theta = np.multiply(self.sh, self.wz) + np.multiply(self.sw, self.ww) + np.multiply(self.ss, self.ws)
        self.cos_theta[self.cos_theta < 0] = 0

        # 计算日射量
        self.Fs = 0.5 + 0.5 * self.cos_tilt
        self.Fg = 1 - self.Fs
        self.I_D = np.multiply(I_dn, self.cos_theta)
        self.I_s = np.multiply(I_sky, self.Fs)
        self.I_hol = np.multiply(I_dn, sun.sin_h) + I_sky
        self.I_r = np.multiply(self.I_hol, rho_g * self.Fg)
        self.I_w = self.I_D + self.I_s + self.I_r

        return self

    # 计算日照得热
    def load_window(self, ags, tau, bn):  # ags是透光面积
        self.CI_D = 3.4167 * self.cos_theta - 4.3890 * self.cos_theta ** 2 + 2.4948 * self.cos_theta ** 3 - 0.5224 * self.cos_theta ** 4
        self.GT = ags * tau * (self.CI_D * self.I_D + 0.91 * (self.I_r + self.I_s))
        self.GA = ags * bn * (self.CI_D * self.I_D + 0.91 * (self.I_r + self.I_s))

        return self

'''
face_1 = Face(112.5, 90)
I = face_1.solar_radiation()
I = face_1.load_window(3.06, 0.48, 0.12)
step = 201 * 24 + 15
print(I.I_D[step], I.I_s[step], I.I_r[step], I.I_w[step], I.GT[step], I.GA[step])
'''






