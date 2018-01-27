# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
"""
全年的任意时间间隔的非定常室内负荷及自然室温的计算
可以在此基础上添加空调设备进行全年的能耗模拟

需要准备的参数
1. 气象参数（全年8760小时的外气温度[℃]，绝对湿度[kg/kg]，法线面直达日射[W/m2]，水平面天空日射[W/m2]，夜间放射[W/m2]）
2. 项目参数（城市，经度，纬度，时区[h]，地面反射率，长波辐射率，外表面日射吸收率）
3. 围护结构参数（窗（面积[m2]，所属，方位角[deg]，倾斜角[deg]，透光面积[m2]，透过率，综合吸收率，贯流传热[W/m2K]）,
                 墙（面积[m2]，所属，邻室，材料[list]，厚度[list[m]]，方位角[deg]，倾斜角[deg]，网格划分[list]））
4. 房间参数（日程，人[W]，照明[W]，设备[W]，室容积[m3]，家具热容量[kJ/K]，换气次数[/h]）

使用流程和实例在最后
"""


# 气象参数
class WeatherData(object):
    """气象参数"""
    def __init__(self, fname, dt):
        self.data = np.loadtxt(fname,  delimiter=",", skiprows=1)
        self.outdoor_temp = self.data[:, 0]
        self.outdoor_ab_humidity = self.data[:, 1]
        self.I_dn = self.data[:, 2]
        self.I_sky = self.data[:, 3]
        self.RN = self.data[:, 4]
        self.dt = dt

        def dt_trans_linear(data, small_dt):
            """定义线性差分，从3600到小间隔"""
            result = list(np.linspace(data[-1], data[0], 3600 // small_dt + 1)[:-1])
            for i in range(len(data) - 1):
                result.extend(list(np.linspace(data[i], data[i + 1], 3600 // small_dt + 1)[:-1]))
            return result

        # map线性差分
        (self.outdoor_temp, self.outdoor_ab_humidity, self.I_dn, self.I_sky,
         self.RN) = map(dt_trans_linear, [self.outdoor_temp, self.outdoor_ab_humidity,
                                          self.I_dn, self.I_sky, self.RN], [self.dt] * 5)


# 角度换算
def d2r(d):
    return np.divide(np.multiply(3.14159265, d), 180)


def r2d(r):
    return np.divide(np.multiply(180, r), 3.14159265)


# 项目信息
class Project(object):
    """项目地址，基本参数，日照参数"""
    def __init__(self, name, latitude, longitude, time_zone, rho_g, epsilon, a_s, weather_data, kc=0.45):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.time_zone = time_zone
        self.rho_g = rho_g
        self.weather_data = weather_data
        self.dt = weather_data.dt
        self.epsilon = epsilon
        self.a_s = a_s
        self.kc = kc
        self.kr = 1 - kc

        # 定量
        self.c_air = 1005
        self.rho_air = 1.2
        self.alpha_i = 8.29
        self.alpha_o = 29.3
        self.r = 2501000

        # 日照
        self.hours = np.linspace(1, 8760, 8760 * 3600 // self.dt)
        self.sin_latitude = np.sin(d2r(self.latitude))
        self.cos_latitude = np.cos(d2r(self.latitude))

        # 计算均时差 真太阳时 时角
        self.b = np.multiply(np.divide(self.hours, 24) - 81, 360/365)
        self.b_r = d2r(self.b)
        self.e = (9.87 * np.sin(2 * self.b_r) - 7.53 * np.cos(self.b_r) - 1.5 * np.sin(self.b_r)) / 60
        self.tas = np.mod(self.hours, 24) + self.e + (self.longitude - 15 * self.time_zone) / 15
        self.omega = np.multiply((self.tas - 12), 15)

        # 计算太阳赤纬
        self.sin_delta = np.multiply(np.sin(self.b_r), 0.397949)
        self.cos_delta = np.cos(np.arcsin(self.sin_delta))

        # 计算太阳高度角
        self.sin_h = (np.multiply(self.sin_latitude, self.sin_delta) +
                      np.multiply(np.multiply(self.cos_latitude, self.cos_delta), np.cos(d2r(self.omega))))
        self.h = r2d(np.arcsin(self.sin_h))
        self.cos_h = np.cos(np.arcsin(self.sin_h))

        # 计算太阳方位角
        self.cos_A = np.divide(np.multiply(self.sin_h, self.sin_latitude) - self.sin_delta,
                               np.multiply(self.cos_h, self.cos_latitude))
        self.A = r2d(np.multiply(np.sign(self.omega), np.arccos(self.cos_A)))
        self.sin_A = np.sin(d2r(self.A))
        if isinstance(self.A, np.ndarray):
            self.h[self.h < 0] = 0
            self.A[self.h == 0] = 0


# 外立面
class Face(object):
    """外立面，计算日射量"""
    def __init__(self, area, room, orientation, tilt, project):
        self.area = area
        self.room = room
        self.orientation = orientation
        self.tilt = tilt
        self.project = project

        # 墙面的三角函数
        self.sin_orientation = np.sin(d2r(self.orientation))
        self.cos_orientation = np.cos(d2r(self.orientation))
        self.sin_tilt = np.sin(d2r(self.tilt))
        self.cos_tilt = np.cos(d2r(self.tilt))

        # 计算入射角
        self.sh = self.project.sin_h
        self.sw = np.multiply(self.project.cos_h, self.project.sin_A)
        self.ss = np.multiply(self.project.cos_h, self.project.cos_A)

        self.wz = self.cos_tilt
        self.ww = np.multiply(self.sin_tilt, self.sin_orientation)
        self.ws = np.multiply(self.sin_tilt, self.cos_orientation)

        self.cos_theta = np.multiply(self.sh, self.wz) + np.multiply(self.sw, self.ww) + np.multiply(self.ss, self.ws)
        self.cos_theta[self.cos_theta < 0] = 0

        # 计算日射量
        self.Fs = 1 / 2 + 1 / 2 * self.cos_tilt
        self.Fg = 1 - self.Fs
        self.I_D = np.multiply(self.project.weather_data.I_dn, self.cos_theta)
        self.I_s = np.multiply(self.project.weather_data.I_sky, self.Fs)
        self.I_hol = np.multiply(self.project.weather_data.I_dn, self.project.sin_h) + self.project.weather_data.I_sky
        self.I_r = np.multiply(self.I_hol, self.project.rho_g * self.Fg)
        self.I_w = self.I_D + self.I_s + self.I_r


# 日照得热在窗，差分法在墙
class Windows(Face):
    windows = []

    def __init__(self, area, room, orientation, tilt, glass_area, tau, bn, k, project):
        self.glass_area = glass_area
        self.tau = tau
        self.bn = bn
        self.k = k
        super().__init__(area, room, orientation, tilt, project)

        self.alpha_0 = self.project.alpha_i
        self.alpha_m = self.project.alpha_o

        self.FI = (1 - self.k / self.alpha_0)
        self.FO = self.k / self.alpha_0
        self.anf = self.area * self.FI

        # 日射热取得
        self.CI_D = (3.4167 * self.cos_theta - 4.3890 * self.cos_theta ** 2 + 2.4948 *
                     self.cos_theta ** 3 - 0.5224 * self.cos_theta ** 4)
        self.GT = self.glass_area * self.tau * (self.CI_D * self.I_D + 0.91 * (self.I_r + self.I_s))
        self.GA = self.glass_area * self.bn * (self.CI_D * self.I_D + 0.91 * (self.I_r + self.I_s))

        # 相当外气温度
        self.te_8760 = (self.GA / self.area / self.k - self.project.epsilon * self.Fs *
                        np.array(self.project.weather_data.RN) / self.alpha_m + self.project.weather_data.outdoor_temp)

        Windows.windows.append(self)


class Walls(Face):
    walls = []

    def __init__(self, area, room, room_by, wall_type, material, depth, orientation, tilt, grid, project):
        self.room_by = room_by  # 邻室名称，非控区域为0
        self.wall_type = wall_type
        self.material = material
        self.depth = depth
        self.grid = grid
        super().__init__(area, room, orientation, tilt, project)

        self.alpha_0 = self.project.alpha_i
        self.alpha_m = {'outer_wall': self.project.alpha_o, 'roof': self.project.alpha_o,
                        'inner_wall': self.project.alpha_i, 'floor': self.project.alpha_i,
                        'ceiling': self.project.alpha_i, 'ground': 9999}[self.wall_type]

        # 差分法
        material_lambda_c_rho = {"concrete": [1.4, 1934], "wood": [0.19, 716], "rock_wool": [0.042, 84],
                                 "alum": [210, 2373], "carpet": [0.08, 318], "stonebodo": [0.17, 1030],
                                 "air": [1 / 0.086, 1], "wood_m": [0.15, 1000], "plasterboard": [0.16, 798],
                                 "fiberglass_quilt": [0.04, 10.08], "wood_siding": [0.14, 477],
                                 "roof_deck": [0.14, 477], "timber_flooring": [0.14, 780], "insulation": [0.04, 0.01],
                                 "concrete_block": [0.51, 1400], "foam_insulation": [0.04, 14],
                                 "concrete_slab": [1.13, 1400]}

        self.r = [1 / self.alpha_0]
        self.cap = [0]
        for i in range(len(self.material)):
            self.r.extend([self.depth[i] / self.grid[i] / material_lambda_c_rho[self.material[i]][0]] * self.grid[i])
            self.cap.extend([self.depth[i] / self.grid[i] *
                             material_lambda_c_rho[self.material[i]][1] * 1000] * self.grid[i])
        self.r.append(1 / self.alpha_m)
        self.cap.append(0)

        self.ul = [self.project.dt * 2 / (self.cap[i] + self.cap[i+1]) / self.r[i] for i in range(sum(grid)+1)]
        self.ur = [self.project.dt * 2 / (self.cap[i] + self.cap[i+1]) / self.r[i+1] for i in range(sum(grid)+1)]

        self.u = np.zeros((sum(grid)+1, sum(grid)+1))
        for i in range(sum(grid)):
            self.u[i][i] = 1 + self.ul[i] + self.ur[i]
            self.u[i+1][i] = - self.ul[i+1]
            self.u[i][i+1] = - self.ur[i]
        self.u[-1][-1] = 1 + self.ul[-1] + self.ur[-1]
        self.ux = np.array(np.matrix(self.u).I)

        self.FI = self.ux[0][0] * self.ul[0]
        self.FO = self.ux[0][-1] * self.ur[-1]
        self.anf = self.area * self.FI

        # 相当外气温度
        if self.wall_type in ('outer_wall', 'roof'):
            self.te_8760 = ((self.project.a_s * self.I_w - self.project.epsilon * self.Fs *
                            np.array(self.project.weather_data.RN)) / self.alpha_m
                            + self.project.weather_data.outdoor_temp)
        elif self.wall_type in 'ground':
            self.te_8760 = [10] * (8760 * 3600 // self.project.dt)

        Walls.walls.append(self)


# 人
class Humans(object):
    humans = []

    def __init__(self, room, n, t, s24, d):
        self.room = room
        self.N_H = n
        self.H_T = t
        self.H_S24 = s24
        self.H_d = d
        self.H_s = 0
        self.H_l = 0
        self.Q_HS = 0
        self.Q_HL = 0
        self.kc = 0.5
        self.kr = 1 - self.kc

        Humans.humans.append(self)

    def load_human(self, indoor_temp):
        """人体发热量和室内温度有关"""
        self.H_s = self.H_S24 - self.H_d * (indoor_temp - 24)
        self.H_l = self.H_T - self.H_s
        self.Q_HS = self.N_H * self.H_s
        self.Q_HL = self.N_H * self.H_l


# 照明
class Lights(object):
    lights = []

    def __init__(self, room, w):
        self.room = room
        self.W_LI = w
        self.kc = 0.4
        self.kr = 1 - self.kc

        Lights.lights.append(self)


# 设备
class Equipments(object):
    equipments = []

    def __init__(self, room, ws, wl):
        """设备有显热和潜热"""
        self.room = room
        self.W_AS = ws
        self.W_AL = wl
        self.kc = 0.4
        self.kr = 1 - self.kc

        Equipments.equipments.append(self)


# 房间
class Rooms(object):
    rooms = []

    def __init__(self, room_name, vol, cpf, n_air, sche, project):
        self.room_name = room_name
        self.VOL = vol
        self.CPF = cpf
        self.n_air = n_air
        self.sche = sche
        self.project = project

        # 定义变量
        self.load_sum_s = 0
        self.load_sum_w = 0
        self.load_max_s = 0
        self.load_max_w = 0

        self.HG_c = 0
        self.HG_r = 0
        self.HLG = 0
        self.GT = 0
        self.AFT = 0
        self.CA = 0
        self.BRM = 0
        self.BRC = 0
        self.BRMX = 0
        self.BRCX = 0
        self.T_mrt = 0

        # 房间构成
        self.windows = [x for x in Windows.windows if x.room == self.room_name]
        self.walls = [x for x in Walls.walls if x.room == self.room_name]
        self.envelope = self.windows + self.walls
        self.humans = [x for x in Humans.humans if x.room == self.room_name]
        self.lights = [x for x in Lights.lights if x.room == self.room_name]
        self.equipments = [x for x in Equipments.equipments if x.room == self.room_name]

        # 房间固有属性
        self.Arm = sum([x.area for x in self.envelope])  # 内表面积和
        self.ANF = sum([x.anf for x in self.envelope])
        self.SDT = self.Arm - self.project.kr * self.ANF
        self.AR = self.Arm * self.project.alpha_i * self.project.kc * (1 - self.project.kc * self.ANF / self.SDT)

        # 内表面吸收率
        for x in self.envelope:
            if "wall_type" in dir(x) and x.wall_type in ('floor', 'ground'):
                x.sn = 0.3 + 0.7 * x.area / self.Arm
            else:
                x.sn = 0.7 * x.area / self.Arm

        # 热容 湿容
        self.RMDT = (self.project.c_air * self.project.rho_air * self.VOL + self.CPF * 1000) / self.project.dt
        self.RMDTX = (self.project.rho_air * self.VOL / self.project.dt)

        # 换气量
        self.Go = self.project.rho_air * self.n_air * self.VOL / 3600

        # 初始条件
        self.indoor_temp = 0
        self.indoor_humidity = 0
        self.ground_temp = 10
        for x in self.walls:
            x.tn = np.ones(np.array(x.ul).shape) * self.indoor_temp
            if x.wall_type is 'ground':
                x.tn = np.ones(np.array(x.ul).shape) * self.ground_temp

    # 循环接口
    def load_cycle(self, step):
        self.HG_c = 0
        self.HG_r = 0
        self.HLG = 0
        self.GT = 0
        self.AFT = 0

        # 室内发热
        if len(self.humans) > 0:
            for x in self.humans:
                x.load_human(self.indoor_temp)
                self.HG_c += x.kc * x.Q_HS * self.sche[step]
                self.HG_r += x.kr * x.Q_HS * self.sche[step]
                self.HLG += x.Q_HL * self.sche[step]
        if len(self.lights) > 0:
            for x in self.lights:
                self.HG_c += x.kc * x.W_LI * self.sche[step]
                self.HG_r += x.kr * x.W_LI * self.sche[step]
        if len(self.equipments) > 0:
            for x in self.equipments:
                self.HG_c += x.kc * x.W_AS * self.sche[step]
                self.HG_r += x.kr * x.W_AS * self.sche[step]
                self.HLG += x.W_AL * self.sche[step]

        # 蓄热
        for x in self.windows:
            x.cf = 0
        for x in self.walls:
            x.cf = np.dot(x.ux[0], x.tn)

        # 室内表面吸收的辐射热
        for x in self.windows:
            self.GT += x.GT[step]
        for x in self.envelope:
            x.rs = x.sn * (self.GT + self.HG_r) / x.area

        # 相当外气温度（注意邻室）
        for x in self.windows:
            x.te = x.te_8760[step]
        for x in self.walls:
            if x.wall_type in ('outer_wall', 'roof', 'ground'):
                x.te = x.te_8760[step]
            if x.wall_type in ('floor', 'ceiling'):
                x.te = self.indoor_temp
            if x.wall_type in 'inner_wall':
                if x.roomby:
                    for y in Rooms.rooms:
                        if x.roomby == y.room_name:
                            x.te = 0.7 * y.indoor_temp + 0.3 * self.project.weather_data.outdoor_temp[step]
                else:
                    x.te = 0.7 * self.indoor_temp + 0.3 * self.project.weather_data.outdoor_temp[step]

        for x in self.envelope:
            x.aft = (x.FO * x.te + x.FI * x.rs / x.alpha_0 + x.cf) * x.area
            self.AFT += x.aft

        # BRM,BRC
        self.CA = self.Arm * self.project.alpha_i * self.project.kc * self.AFT / self.SDT
        self.BRM = self.RMDT + self.AR + self.project.c_air * self.Go
        self.BRC = (self.RMDT * self.indoor_temp + self.CA + self.project.c_air
                    * self.Go * self.project.weather_data.outdoor_temp[step] + self.HG_c)
        self.BRMX = self.RMDTX + self.Go
        self.BRCX = (self.RMDTX * self.indoor_humidity + self.Go * self.project.weather_data.outdoor_ab_humidity[step]
                     + self.HLG / self.project.r)
        self.indoor_temp = self.BRC / self.BRM
        self.indoor_humidity = self.BRCX / self.BRMX

        # 后处理
        self.T_mrt = (self.project.kc * self.ANF * self.indoor_temp + self.AFT) / self.SDT
        for x in self.windows:
            x.T_sn = self.indoor_temp - (self.indoor_temp - self.project.weather_data.outdoor_temp[step]) \
                                        * x.k / x.alpha_0
        for x in self.walls:
            x.tn[0] += x.ul[0] * (self.project.kc * self.indoor_temp + self.project.kr
                                  * self.T_mrt + x.rs / x.alpha_0)
            x.tn[-1] += x.ur[-1] * x.te
            x.tn = np.dot(x.ux, x.tn)
            x.T_sn = x.tn[0]


# 使用流程（实例）
# 1. 读取气象参数
# 气象参数从csv文件读取，不要有数字以外的内容，数据从第二行开始，一共（8760行 + 1行） * 5列
# 360的单位是秒，代表时间间隔，理论上可以取任意小于等于3600的正数，但最好是能够被3600整除
wea = WeatherData("input_data/DRYCOLD01.csv", 360)
# 2. 输入项目信息
# 城市，经度，纬度，时区[h]，地面反射率，长波辐射率，外表面日射吸收率，气象参数
project_1 = Project('USCO', 39.8, -104.9, -6, 0.2, 0.9, 0.6, wea)
# 3. 输入围护结构参数
# 面积[m2]，所属，方位角[deg]，倾斜角[deg]，透光面积[m2]，透过率，综合吸收率，贯流传热[W/m2K]，项目信息
window_1 = Windows(12, 'room_1', 0, 90, 12, 0.7469, 0.04355, 3, project_1)
# 面积[m2]，所属，邻室，材料[list]，厚度[list[m]]，方位角[deg]，倾斜角[deg]，网格划分[list]，项目信息
wall_1 = Walls(9.6, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 0, 90, [12, 10, 2], project_1)
wall_2 = Walls(16.2, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -90, 90, [12, 10, 2], project_1)
wall_3 = Walls(21.6, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -180, 90, [12, 10, 2], project_1)
wall_4 = Walls(16.2, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 90, 90, [12, 10, 2], project_1)
wall_5 = Walls(48, 'room_1', 0, 'roof', ["plasterboard", "fiberglass_quilt", "roof_deck"],
               [0.01, 0.1118, 0.019], 0, 0, [2, 10, 4], project_1)
wall_6 = Walls(48, 'room_1', 0, 'ground', ["concrete_slab", "insulation"], [0.080, 1.007], 0, 0, [12, 15], project_1)
# 4. 输入房间参数
# 日程 一个list，()中是长度
schedule_1 = [1] * (8760 * 3600 // project_1.dt)
# 所属，发热量
light_1 = Lights('room_1', 200)
# 房间名，室容积[m3]，家具热容量[kJ/K]，换气次数[/h]，日程，项目信息
room_1 = Rooms('room_1', 129.6, 0, 0.5, schedule_1, project_1)
# 5. 循环开始
output = []
for cal_step in range(8760 * 3600 // project_1.dt):
    room_1.load_cycle(cal_step)  # 循环方法
    output.append(room_1.indoor_humidity)
plt.plot(output)
plt.plot(room_1.project.weather_data.outdoor_ab_humidity)
plt.show()
