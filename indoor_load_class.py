# -*- coding: utf-8 -*-
import numpy as np
import difference_methods
import readcsv
import sun_class
import matplotlib.pyplot as plt
## 热负荷计算programme

# 1. input
# 时间间隔
dt = 3600
# 表面换热系数
alpha_i = 9.3
alpha_o = 23
# 对流和辐射的比例
kc = 0.45
kr = 0.55
# 长波辐射率
epsilon = 0.9
# 综合外壁特性
Fs = 0.5  # 天空的水平面和前直面的比例
rho_g = 0.2  # 地面反射率
a_s = 0.7  # 外表面日射吸收率
# 空气特性
c_air = 1.005
rho_air = 1.2
# 气象参数
weather_data = readcsv.weather()
RN = weather_data["RN"]
x = weather_data["x"]
outdoor_temp = weather_data["outdoor_temp"]

# 1.1 壁体
# 定义窗
class Windows(sun_class.Face):
    sum_area = 0
    windows = []

    def __init__(self, area, room, orientation, tilt, glass_area, tau, bn, k):
        self.area = area  # 面积
        self.room = room  # 房间
        self.orientation = orientation  # 朝向
        self.tilt = tilt  # 倾斜角
        self.glass_area = glass_area  # 玻璃面积
        self.tau = tau  # 投光率
        self.bn = bn  # 吸收日射取得率
        self.k = k  # 贯流

        self.alpha_0 = alpha_i  # 窗内表面换热系数
        self.alpha_m = alpha_o  # 窗外表面换热系数

        self.FI = (1 - self.k / alpha_i)  # 差分法FI
        self.FO = self.k / alpha_i  # 差分法FO
        self.anf = self.area * self.FI

        # 日射热取得
        # 窗的GO是不需要的，因为贯流是一起算的？
        self = self.solar_radiation()
        self = self.load_window(self.glass_area, self.tau, self.bn)
        # self.GT, self.GA, self.GO = load_window.load_window(26, self.orientation, self.tilt, self.area, self.glass_area / self.area, self.tau, self.bn, self.k)

        # 相当外气温度
        self.te_8760 = self.GA / self.area / self.k - epsilon * Fs * RN / alpha_o + outdoor_temp
        # GA肯定有问题！

        Windows.sum_area += self.area  # 统计面积
        Windows.windows.append(self)  # 生成列表


# 输入
window_1 = Windows(28, 'room_1', 45, 90, 24, 0.79, 0.04, 6.4)
window_2 = Windows(28, 'room_2', 45, 90, 24, 0.79, 0.04, 6.4)


#print(outdoor_temp[4800:4824], window_1.te[4800:4824])
# 定义墙
class Walls(sun_class.Face):
    sum_area = 0
    walls = []

    def __init__(self, area, room, wall_type, material, depth, orientation, tilt, grid):
        self.area = area  # 面积
        self.room = room  # 房间
        self.wall_type = wall_type  # 类型
        self.material = material  # 材质
        self.depth = depth  # 厚度
        self.orientation = orientation  # 朝向
        self.tilt = tilt  # 倾斜角
        self.grid = grid  # 网格划分

        self.alpha_0 = alpha_i  # 内表面换热系数

        # 外表面换热系数
        if self.wall_type in ('outer_wall', 'roof', 'ground'):
            self.alpha_m = alpha_o
        elif self.wall_type in ('inner_wall', 'floor', 'ceiling'):
            self.alpha_m = alpha_i

        # 差分法调用
        self.ul, self.ur, self.ux = difference_methods.diff_ux(self.material, self.depth, self.grid, dt, self.alpha_0, self.alpha_m)
        self.FI = self.ux[0][0] * self.ul[0]
        self.FO = self.ux[0][-1] * self.ur[-1]
        self.anf = self.area * self.FI

        # 日射量 (仅针对外墙)
        if self.wall_type in ('outer_wall', 'roof'):
            self = self.solar_radiation()
            # self.I_w = solar_radiation.i_w(self.orientation, self.tilt)
            self.te_8760 = (a_s * self.I_w - epsilon * Fs * RN) / alpha_o + outdoor_temp  # 相当外气温度
        if self.wall_type in ('ground'):
            self.te_8760 = outdoor_temp  # 土地？

        Walls.sum_area += self.area  # 统计面积
        Walls.walls.append(self)  # 生成列表


# 输入
wall_1 = Walls(22.4, 'room_1', 'outer_wall', ["concrete", "rock_wool", "air", "alum"], [0.150, 0.050, 0, 0.002], 45, 90, [7, 2, 1, 1])
wall_2 = Walls(100.8, 'room_1', 'inner_wall', ["concrete"], [0.120], 0, 90, [6])
wall_3 = Walls(98, 'room_1', 'floor',  ["carpet", "concrete", "air", "stonebodo"], [0.015, 0.150, 0, 0.012], 0, 0, [1, 7, 1, 1])
wall_4 = Walls(98, 'room_1', 'ceiling', ["stonebodo", "air", "concrete", "carpet"], [0.012, 0, 0.150, 0.015], 0, 0, [1, 1, 7, 1])


class Schedule(object):
    sche = [0] * 8 + [1] * 12 + [0] * 4
    sche_year = sche * 365

sche_year = Schedule().sche_year


class Humans(object):
    humans = []

    def __init__(self, room, n, t, s24, d):
        self.room = room
        self.N_H = n
        self.H_T = t
        self.H_S24 = s24
        self.H_d = d

        Humans.humans.append(self)

    # 通过室内温度求人体发热量
    def load_human(self, indoor_temp):
        self.H_s = self.H_S24 - self.H_d * (indoor_temp - 24)
        self.H_l = self.H_T - self.H_s
        self.Q_HS = self.N_H * self.H_s
        self.Q_HL = self.N_H * self.H_l
        return self

human_1 = Humans('room_1', 16, 119, 62, 4)


class Lights(object):
    lights = []

    def __init__(self, room, w):
        self.room = room
        self.W_LI = w

        Lights.lights.append(self)

light_1 = Lights('room_1', 2900)


class Equipments(object):
    equipments = []

    def __init__(self, room, ws, wl):
        self.room = room
        self.W_AS = ws
        self.W_AL = wl

        Equipments.equipments.append(self)

equipment_1 = Equipments('room_1', 500, 0)


# 定义房间
class Room(object):

    def __init__(self, room_name, vol, cpf, n_air):
        self.room_name = room_name
        self.VOL = vol  # 室容积
        self.CPF = cpf  # 热容量
        self.n_air = n_air  # 换气次数
        self.windows = [x for x in Windows.windows if x.room == self.room_name]  # 找窗
        self.walls = [x for x in Walls.walls if x.room == self.room_name]  # 找墙
        self.envelope = self.windows + self.walls  # 围护
        self.humans = [x for x in Humans.humans if x.room == self.room_name]
        self.lights = [x for x in Lights.lights if x.room == self.room_name]
        self.equipments = [x for x in Equipments.equipments if x.room == self.room_name]

        self.Arm = sum([x.area for x in self.envelope])  # 内表面积和
        self.ANF = sum([x.anf for x in self.envelope])
        self.SDT = self.Arm - kr * self.ANF
        self.AR = self.Arm * alpha_i * kc * (1 - kc * self.ANF / self.SDT)

        # 重要：只有在房间里的面才有sn，所以之前的对象不需要sn属性
        for x in self.windows:
            x.sn = 0.7 * x.area / self.Arm
        for x in self.walls:
            if x.wall_type == 'floor':
                x.sn = 0.3 + 0.7 * x.area / self.Arm
            else:
                x.sn = 0.7 * x.area / self.Arm

        self.RMDT = (c_air * rho_air * self.VOL + self.CPF * 1000) / dt
        self.Go = rho_air * self.n_air * self.VOL / 3600  # 间隙风

        # 初始条件
        self.indoor_temp = 5
        for x in self.walls:
            x.tn = np.ones(np.array(x.ul).shape) * self.indoor_temp

    # 室内发热成分
    def heat_generate(self, step):
        self.humans[0] = self.humans[0].load_human(self.indoor_temp)  # 限制了一个房间只有一种人
        self.HG_c = (0.5 * self.humans[0].Q_HS + 0.6 * self.lights[0].W_LI + 0.6 * self.equipments[0].W_AS) * sche_year[step]
        self.HG_r = (0.5 * self.humans[0].Q_HS + 0.4 * self.lights[0].W_LI + 0.4 * self.equipments[0].W_AS) * sche_year[step]
        self.HLG = (self.humans[0].Q_HL + self.equipments[0].W_AL) * sche_year[step]
        return self

    def cf_cal(self, step):
        for x in self.windows:
            x.cf = 0  # 定常
        for x in self.walls:
            x.cf = np.dot(x.ux[0], x.tn)  # CF 围护的前一个时刻的影响
        for x in self.envelope:
            x.rs = x.sn * (self.windows[0].GT[step] + self.HG_r) / x.area  # 室内表面吸收的辐射热
        return self

    # 相当外气温度(内壁)  (外壁还是list的形式)
    def te_indoor(self, step):
        self.AFT = 0
        for x in self.windows:
            x.te = x.te_8760[step]
        for x in self.walls:
            if x.wall_type in ('outer_wall', 'roof', 'ground'):
                x.te = x.te_8760[step]
            if x.wall_type == 'inner_wall':
                x.te = 0.7 * self.indoor_temp + 0.3 * outdoor_temp[step]
            if x.wall_type in ('floor', 'ceiling'):
                x.te = self.indoor_temp
        for x in self.envelope:
            x.aft = (x.FO * x.te + x.FI * x.rs / alpha_i + x.cf) * x.area
            self.AFT += x.aft
        return self

    # 计算indoor_temp
    def indoor_temp_cal(self, step):
        temp0 = self.indoor_temp
        self.CA = self.Arm * alpha_i * kc * self.AFT / self.SDT
        self.BRM = self.RMDT + self.AR + 1005 * self.Go
        self.BRC = self.RMDT * self.indoor_temp + self.CA + 1005 * self.Go * outdoor_temp[step] + self.HG_c
        self.indoor_temp = self.BRC / self.BRM
        self.delta_indoor_temp = self.indoor_temp - temp0
        return self

    # 后处理
    def after_cal(self):
        self.T_mrt = (kc * self.ANF * self.indoor_temp + self.AFT) / self.SDT
        for x in self.windows:
            x.T_sn = self.indoor_temp - (self.indoor_temp - outdoor_temp[step]) * x.k / alpha_i
            x.q0 = alpha_i * (self.indoor_temp - x.T_sn)
        for x in self.walls:
            x.tn[0] += x.ul[0] * self.indoor_temp
            x.tn[-1] += x.ur[-1] * x.te
            x.tn = np.dot(x.ux, x.tn)
            x.T_sn = x.tn[0]
            x.q0 = alpha_i * (self.indoor_temp - x.T_sn)
        return self


room_1 = Room('room_1', 353, 3500, 0.2)


# 循环开始
output = []
for step in range(240):
    room_1 = room_1.heat_generate(step)
    room_1 = room_1.cf_cal(step)
    room_1 = room_1.te_indoor(step)
    room_1 = room_1.indoor_temp_cal(step)
    room_1 = room_1.after_cal()
    output.append(room_1.indoor_temp)


plt.plot(outdoor_temp[:240])
plt.plot(output)
plt.show()
