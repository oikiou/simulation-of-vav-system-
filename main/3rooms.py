# -*- coding:utf-8 -*-
from roomload import *

# project
wea = WeatherData("input_data/DRYCOLD01.csv", 3600)
project_1 = Project('USCO', 39.8, -104.9, -6, 0.2, 0.9, 0.6, wea)
# room_1
window_11 = Windows(12, 'room_1', 0, 90, 12, 0.7469, 0.04355, 3, project_1)
window_12 = Windows(12, 'room_1', -90, 90, 12, 0.7469, 0.04355, 3, project_1)
wall_11 = Walls(9.6, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 0, 90, [12, 10, 2], project_1)
wall_12 = Walls(4.2, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -90, 90, [12, 10, 2], project_1)
wall_13 = Walls(21.6, 'room_1', 0, 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -180, 90, [12, 10, 2], project_1)
wall_14 = Walls(16.2, 'room_1', 'room_2', 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 90, 90, [12, 10, 2], project_1)
wall_15 = Walls(48, 'room_1', 0, 'roof', ["plasterboard", "fiberglass_quilt", "roof_deck"],
               [0.01, 0.1118, 0.019], 0, 0, [2, 10, 4], project_1)
wall_16 = Walls(48, 'room_1', 0, 'ground', ["concrete_slab", "insulation"], [0.080, 1.007], 0, 0, [12, 15], project_1)
schedule_1 = [1] * (8760 * 3600 // project_1.dt)
light_1 = Lights('room_1', 200)
room_1 = Rooms('room_1', 129.6, 0, 0.5, schedule_1, project_1)
# room_2
window_21 = Windows(12, 'room_2', 0, 90, 12, 0.7469, 0.04355, 3, project_1)
wall_21 = Walls(9.6, 'room_2', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 0, 90, [12, 10, 2], project_1)
wall_22 = Walls(16.2, 'room_2', 'room_1', 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -90, 90, [12, 10, 2], project_1)
wall_23 = Walls(21.6, 'room_2', 0, 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -180, 90, [12, 10, 2], project_1)
wall_24 = Walls(16.2, 'room_2', 'room_3', 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 90, 90, [12, 10, 2], project_1)
wall_25 = Walls(48, 'room_2', 0, 'roof', ["plasterboard", "fiberglass_quilt", "roof_deck"],
               [0.01, 0.1118, 0.019], 0, 0, [2, 10, 4], project_1)
wall_26 = Walls(48, 'room_2', 0, 'ground', ["concrete_slab", "insulation"], [0.080, 1.007], 0, 0, [12, 15], project_1)
schedule_2 = [1] * (8760 * 3600 // project_1.dt)
light_2 = Lights('room_2', 200)
room_2 = Rooms('room_2', 129.6, 0, 0.5, schedule_2, project_1)
# room_3
window_31 = Windows(12, 'room_3', 0, 90, 12, 0.7469, 0.04355, 3, project_1)
window_32 = Windows(12, 'room_3', 90, 90, 12, 0.7469, 0.04355, 3, project_1)
wall_31 = Walls(9.6, 'room_3', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 0, 90, [12, 10, 2], project_1)
wall_32 = Walls(16.2, 'room_3', 'room_2', 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -90, 90, [12, 10, 2], project_1)
wall_33 = Walls(21.6, 'room_3', 0, 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -180, 90, [12, 10, 2], project_1)
wall_34 = Walls(4.2, 'room_3', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 90, 90, [12, 10, 2], project_1)
wall_35 = Walls(48, 'room_3', 0, 'roof', ["plasterboard", "fiberglass_quilt", "roof_deck"],
               [0.01, 0.1118, 0.019], 0, 0, [2, 10, 4], project_1)
wall_36 = Walls(48, 'room_3', 0, 'ground', ["concrete_slab", "insulation"], [0.080, 1.007], 0, 0, [12, 15], project_1)
schedule_3 = [1] * (8760 * 3600 // project_1.dt)
light_3 = Lights('room_3', 200)
room_3 = Rooms('room_3', 129.6, 0, 0.5, schedule_3, project_1)

output1 = []
output2 = []
output3 = []
for cal_step in range(8760 * 3600 // project_1.dt):
    room_1.load_cycle(cal_step)  # 循环方法
    room_2.load_cycle(cal_step)
    room_3.load_cycle(cal_step)
    output1.append(room_1.indoor_temp)
    output2.append(room_2.indoor_temp)
    output3.append(room_3.indoor_temp)
plt.plot(output1)
plt.plot(output2)
plt.plot(output3)
# plt.plot(room_1.project.weather_data.outdoor_temp)
plt.show()
#np.savetxt('output/1-4.csv', output, delimiter = ',', fmt="%.4f")