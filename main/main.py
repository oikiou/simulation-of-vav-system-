# -*- coding: utf-8 -*-
from roomload import *


# 气象(气象参数地址，时间间隔)
wea = WeatherData("input_data/DRYCOLD01.csv", 60)
# 城市(名字，经纬度，时区，地面反射率，长波辐射率，外表面日射吸收率，气象参数)
# project = Project('tokyo', 35.68, 139.77, 9, 0.2, 0.9, 0.6, wea)
project = Project('USCO', 39.8, -104.9, -6, 0.2, 0.9, 0.6, wea)

# 房间1
# 窗
window_1 = Windows(12, 'room_1', 0, 90, 12, 0.7469, 0.04355, 3, project)
# 墙
wall_1 = Walls(9.6, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"], [0.1, 0.0615, 0.009], 0, 90, [12, 10, 2], project)
wall_2 = Walls(16.2, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"], [0.1, 0.0615, 0.009], -90, 90, [12, 10, 2], project)
wall_3 = Walls(21.6, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"], [0.1, 0.0615, 0.009], -180, 90, [12, 10, 2], project)
wall_4 = Walls(16.2, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"], [0.1, 0.0615, 0.009], 90, 90, [12, 10, 2], project)
wall_5 = Walls(48, 'room_1', 0, 'roof', ["plasterboard", "fiberglass_quilt", "roof_deck"], [0.01, 0.1118, 0.019], 0, 0, [2, 10, 4], project)
wall_6 = Walls(48, 'room_1', 0, 'ground', ["concrete_slab", "insulation"], [0.080, 1.007], 0, 0, [12, 15], project)
# 日程表
sche = [1] * (8760 * 3600 // project.dt)
# 人
human_1 = Humans('room_1', 16, 119, 62, 4)
# 照明
light_1 = Lights('room_1', 200)
# 设备
equipment_1 = Equipments('room_1', 500, 0)
# 房间
room_1 = Rooms('room_1', 129.6, 0, 0.5, sche, project)


print([room_1.envelope[i].sn for i in range(len(room_1.envelope))])
'''

a = [1,2]
#print(dir(a))

class A(object):
    def __init__(self):
        self.wall_type = 1

class B(object):
    def __init__(self):
        pass

a = A()
b = B()

if "wall_type" in dir(a) and a.wall_type ==1:
    print(True)

if "wall_type" in dir(b) and b.wall_type ==1:
    print(True)
'''