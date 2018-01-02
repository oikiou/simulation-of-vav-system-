# -*- coding: utf-8 -*-
import numpy as np
import difference_methods
import readcsv
import load_window
import solar_radiation
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
class Windows(object):
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

        Windows.sum_area += self.area  # 统计面积
        Windows.windows.append(self)  # 生成列表

        # 日射热取得
        # 窗的GO是不需要的，因为贯流是一起算的？
        self.GT, self.GA, self.GO = load_window.load_window(26, self.orientation, self.tilt, self.area, self.glass_area / self.area, self.tau, self.bn, self.k)
        # 这个def需要检查！！

        # 相当外气温度
        self.te = self.GA / self.area / self.k - epsilon * Fs * RN / alpha_o + outdoor_temp
        # GA肯定有问题！


# 输入
window_1 = Windows(28, 'room_1', 45, 90, 24, 0.79, 0.04, 6.4)
window_2 = Windows(28, 'room_2', 45, 90, 24, 0.79, 0.04, 6.4)

print(outdoor_temp[4800:4824], window_1.te[4800:4824])
# 定义墙
class Walls(object):
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

        Walls.sum_area += self.area  # 统计面积
        Walls.walls.append(self)  # 生成列表

        # 日射量
        if self.wall_type in ('outer_wall', 'roof'):
            self.I_w = solar_radiation.i_w(self.orientation, self.tilt)

        # 相当外气温度
        # 外墙


# 输入
wall_1 = Walls(22.4, 'room_1', 'outer_wall', ["concrete", "rock_wool", "air", "alum"], [0.150, 0.050, 0, 0.002], 45, 90, [7, 2, 1, 1])
wall_2 = Walls(100.8, 'room_1', 'inner_wall', ["concrete"], [0.120], 0, 0, [6])
wall_3 = Walls(98, 'room_1', 'floor',  ["carpet", "concrete", "air", "stonebodo"], [0.015, 0.150, 0, 0.012], 0, 0, [1, 7, 1, 1])
wall_4 = Walls(98, 'room_1', 'ceiling', ["stonebodo", "air", "concrete", "carpet"], [0.012, 0, 0.150, 0.015], 0, 0, [1, 1, 7, 1])


class Human(object):
    # 人数
    # 体表面积
    # 发热量
    # 时刻表
    def __init__(self, n, t, s24, d):
        self.N_H = n
        self.H_T = t
        self.H_S24 = s24
        self.H_d = d

    # 通过室内温度求人体发热量
    def t_h(self, indoor_temp):
        pass

human_1 = Human(16, 119, 62, 4)


class Light(object):

    def __init__(self, w):
        self.W_LI = w

light_1 = Light(2900)


class Equipment(object):

    def __init__(self, ws, wl):
        self.W_AS = ws
        self.W_AL = wl

equipment_1 = Equipment(500, 0)


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

room_1 = Room('room_1', 353, 3500, 0.2)
#print(room_1.ANF)
#print([x.sn for x in room_1.envelope])




