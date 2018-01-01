# -*- coding: utf-8 -*-
import numpy as np
import difference_methods

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

        self.FI = (1 - self.k) / alpha_i  # 差分法FI
        self.FO = self.k / alpha_i  # 差分法FO

        Windows.sum_area += self.area
        Windows.windows.append(self)

window_1 = Windows(28, 'room_1', 45, 0, 24, 0.79, 0.04, 6.4)
window_2 = Windows(28, 'room_2', 45, 0, 24, 0.79, 0.04, 6.4)


class Walls(object):
    sum_area = 0
    walls = []

    def __init__(self, area, room, wall_type, material, depth, orientation, tilt, grid):
        self.area = area
        self.room = room
        self.wall_type = wall_type
        self.material = material
        self.depth = depth
        self.orientation = orientation
        self.tilt = tilt
        self.grid = grid

        self.alpha_0 = alpha_i

        if self.wall_type in ('outer_wall', 'roof', 'ground'):
            self.alpha_m = alpha_o
        elif self.wall_type in ('inner_wall', 'floor', 'ceiling'):
            self.alpha_m = alpha_i

        self.ul, self.ur, self.ux = difference_methods.diff_ux(self.material, self.depth, self.grid, dt, self.alpha_0, self.alpha_m)
        self.FI = self.ux[0][0] * self.ul[0]
        self.FO = self.ux[0][-1] * self.ur[-1]

        Walls.sum_area += self.area
        Walls.walls.append(self)

wall_1 = Walls(22.4, 'room_1', 'outer_wall', ["concrete", "rock_wool", "air", "alum"], [0.150, 0.050, 0, 0.002], 45, 0, [7, 2, 1, 1])
wall_2 = Walls(100.8, 'room_1', 'inner_wall', ["concrete"], [0.120], 0, 0, [6])
wall_3 = Walls(98, 'room_1', 'floor',  ["carpet", "concrete", "air", "stonebodo"], [0.015, 0.150, 0, 0.012], 0, 0, [1, 7, 1, 1])
wall_4 = Walls(98, 'room_1', 'ceiling', ["stonebodo", "air", "concrete", "carpet"], [0.012, 0, 0.150, 0.015], 0, 0, [1, 1, 7, 1])


class Human(object):
    # 人数
    # 体表面积
    # 发热量
    # 时刻表
    pass


class Room(object):

    def __init__(self, windows, walls):
        self.windows = windows
        self.walls = walls
        self.envelope = self.windows + self.walls
        self.Arm = sum([x.area for x in self.envelope])  # 内表面积和

room_1 = Room([x for x in Windows.windows if x.room == 'room_1'], [x for x in Walls.walls if x.room == 'room_1'])
print(room_1.Arm)


