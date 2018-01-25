# -*- coding: utf-8 -*-
import numpy as np


class WeatherData(object):
    "气象参数"
    def __init__(self, fname):
        self.data = np.loadtxt(fname,  delimiter=",", skiprows=1)
        self.outdoor_temp = self.data[:, 0]
        self.outdoor_ab_humidity = self.data[:, 1]
        self.I_dn = self.data[:, 2]
        self.I_sky = self.data[:, 3]
        self.RN = self.data[:, 4]

    def data_trans(self, dt):
        "对所有的数据的时间间隔进行变化"

        def dt_trans_linear(data, dt):
            "定义线性差分，从3600到小间隔"
            result = np.linspace(data[-1], data[0], 3600 // dt + 1)[:-1]
            for i in range(len(data) - 1):
                result.extend(np.linspace(data[i], data[i + 1], 3600 // dt + 1)[:-1])
            return result

        self.outdoor_temp = dt_trans_linear(self.outdoor_temp, dt)
        self.outdoor_ab_humidity = dt_trans_linear(self.outdoor_ab_humidity, dt)
        self.I_dn = dt_trans_linear(self.I_dn, dt)
        self.I_sky = dt_trans_linear(self.I_sky, dt)
        self.RN = dt_trans_linear(self.RN, dt)

#w = WeatherData("input_data/DRYCOLD01.csv")
#print(w.outdoor_temp[7])


