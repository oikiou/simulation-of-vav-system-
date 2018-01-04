# -*- coding: utf-8 -*-
import numpy as np
import readcsv

# 直达日射 水平面天空日射 夜间放射
weather_data = readcsv.weather()
I_dn = weather_data["I_dn"]
I_sky = weather_data["I_sky"]
rho = 0.2  # 地面反射


def d2r(d):
    return np.divide(np.multiply(3.14159265, d), 180)


def r2d(r):
    return np.divide(np.multiply(180, r), 3.14159265)


# 城市
class Citys(object):

    def __init__(self, name, latitude, longitude, time_zone):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.time_zone = time_zone

tokyo = Citys('tokyo', 35.68, 139.77, 9)
usco = Citys('USCO', 39.76, -134.86, -6)


# 太阳方位角和高度角的计算
# 输入为城市
# 输出为sun.h, sun.A
class Sun(object):
    '太阳日射，知道城市的经纬度和时区，自动生成全年或一段时间的太阳高度角和方位角'
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
        if isinstance(self.A, np.ndarray):
            self.h[self.h < 0] = 0
            self.A[self.h == 0] = 0


#sun_1 = Sun(tokyo, [x for x in range(201*24,201*24+23)])
#print(sun_1.h, sun_1.A)

class face(object):
    '外墙和外窗继承自face，有日照相关的参数'
    pass



