# -*- coding:utf-8 -*-
from roomload import *


# project
wea = WeatherData("input_data/DRYCOLD01.csv", 3600)
project_1 = Project('USCO', 39.8, -104.9, -6, 0.2, 0.9, 0.6, wea)
# room_1
window_1 = Windows(12, 'room_1', 0, 90, 12, 0.7469, 0.04355, 3, project_1)
window_2 = Windows(12, 'room_1', -90, 90, 12, 0.7469, 0.04355, 3, project_1)
wall_1 = Walls(9.6, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 0, 90, [12, 10, 2], project_1)
wall_2 = Walls(4.2, 'room_1', 0, 'outer_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -90, 90, [12, 10, 2], project_1)
wall_3 = Walls(21.6, 'room_1', 0, 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], -180, 90, [12, 10, 2], project_1)
wall_4 = Walls(16.2, 'room_1', 'room_2', 'inner_wall', ["concrete_block", "foam_insulation", "wood_siding"],
               [0.1, 0.0615, 0.009], 90, 90, [12, 10, 2], project_1)
wall_5 = Walls(48, 'room_1', 0, 'roof', ["plasterboard", "fiberglass_quilt", "roof_deck"],
               [0.01, 0.1118, 0.019], 0, 0, [2, 10, 4], project_1)
wall_6 = Walls(48, 'room_1', 0, 'ground', ["concrete_slab", "insulation"], [0.080, 1.007], 0, 0, [12, 15], project_1)
schedule_1 = [1] * (8760 * 3600 // project_1.dt)
light_1 = Lights('room_1', 200)
room_1 = Rooms('room_1', 129.6, 0, 0.5, schedule_1, project_1)




output = []
for cal_step in range(8760 * 3600 // project_1.dt):
    room_1.load_cycle(cal_step)  # 循环方法
    output.append(room_1.indoor_temp)
#plt.plot(output)
#plt.plot(room_1.project.weather_data.outdoor_temp)
#plt.show()
#np.savetxt('output/1-4.csv', output, delimiter = ',', fmt="%.4f")