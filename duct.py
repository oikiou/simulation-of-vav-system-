# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from duct_class import *

# 三个房间的VAV风阀 和 空调箱的三个风阀
vav1 = Damper(0.35)
vav2 = Damper(0.3)
vav3 = Damper(0.4)
fresh_air_damper = Damper(0.6)
exhaust_air_damper = Damper(0.6)
mix_air_damper = Damper(0.6)

# 送风管段
duct_1 = Duct(1547, 10, 0.05+0.1+0.23+0.4+0.9+1.2+0.23, damper=vav1)
duct_2 = Duct(1140, 2.5, 0.3+0.1+0.4+0.23+1.2+0.9, damper=vav2)
duct_12 = Duct(1547 + 1140, 7.5, 0.05+0.1, a=0.5)
duct_3 = Duct(1872, 2.5, 0.3+0.1+0.4+0.23+1.2+0.9, damper=vav3)
duct_123 = Duct(1547 + 1140 + 1872, 4.3, 3.6+0.23, a=0.5)
# 回风管段
duct_return_air = Duct(4342, 1.75, 0.5+0.24, a=0.6)
duct_exhaust_air = Duct(4342, 0.95, 3.7+0.9+0.4+0.05, damper=exhaust_air_damper, a=0.6)
duct_fresh_air = Duct(4342, 0.78, 1.4+0.1+0.4, damper=fresh_air_damper, a=0.6)
duct_mix_air = Duct(4342, 2.2, 0.3+0.4+1.5, damper=mix_air_damper, a=0.6)

# 风机
g = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]
p = [[443, 383, 348, 305, 277, 249, 216, 172, 112, 30]]
p.append([355, 296, 256, 238, 207, 182, 148, 97, 21])
p.append([342, 284, 246, 217, 190, 161, 121, 62])
p.append([336, 278, 236, 206, 178, 145, 97, 38])
p.append([320, 264, 223, 189, 153, 109, 50])
p.append([300, 239, 194, 153, 110, 55])
p.append([260, 200, 152, 107, 52])
p.append([179, 129, 79, 24])
# 送回风机
g1 = list(map(lambda x: x * 4342 / 1200, g))
p1 = [[x * 40 / 216 for x in pi] for pi in p]
f1 = Fan(g1, p1)  # 回风机
g2 = list(map(lambda x: x * 4342 / 1200, g))
p2 = [[x * 350 / 216 for x in pi] for pi in p]
f2 = Fan(g2, p2)  # 送风机
#f1.plot()

# 送风管
duct_supply_air = Serial(duct_123, Parallel(duct_3, Serial(duct_12, Parallel(duct_1, duct_2))))


# 整合
def all_balanced(inv_f_r, inv_f_s, v1, v2, v3, ve, vm, vf):
    f1.inv = inv_f_r
    f2.inv = inv_f_s
    vav1.theta_run(v1)
    vav2.theta_run(v2)
    vav3.theta_run(v3)
    exhaust_air_damper.theta_run(ve)
    mix_air_damper.theta_run(vm)
    fresh_air_damper.theta_run(vf)
    duct_1.s_cal()
    duct_2.s_cal()
    duct_3.s_cal()
    duct_fresh_air.s_cal()
    duct_return_air.s_cal()
    duct_mix_air.s_cal()
    duct_exhaust_air.s_cal()
    duct_supply_air.s_cal()
    duct_system.balance()
    duct_system.balance_check()
    duct_supply_air.g_cal(duct_system.g_supply_air)
    #print(duct_1.g, duct_2.g, duct_3.g)

# 风管系统
duct_system = DuctSystem(duct_supply_air, duct_return_air, duct_exhaust_air, duct_fresh_air, duct_mix_air, f2, f1)

inv_f = 50
inv_s = 50
v1 = 0
v2 = 0
v3 = 0
ve = 35
vm = 10
vf = 35

'''
for i in range(10):
    print(i)
    input = ([x * 25 + 25 for x in np.random.rand(2)] + [x * 40 + 10 for x in np.random.rand(6)])
    print(input)

    all_balanced(input[0], input[1], input[2], input[3], input[4], input[5], input[6], input[7])
#all_balanced(inv_f, inv_s, v1, v2, v3, ve, vm, vf)
# all_balanced(47.166480340756159, 48.367742212475271, 36.943781158385818, 11.662012052094699, 45.266316207053585, 20.424508626582988, 10.358618215473587, 12.473039701154626)
'''

# 控制逻辑

input = [3.1062, 1.5403, 1.6868,
4.0044,	2.7063,	2.9454,
4.2974,	3.4723,	3.7323,
4.5034,	3.886,	4.3607,
4.3603,	3.8901,	4.9772,
3.9899,	3.6637,	5.431,
3.099, 2.9209,	4.8768,
2.1931,	2.118,	3.6286,
1.3673,	1.3961,	2.1414,
0.9267,	1.0217,	1.5211,
0.5737,	0.7273,	1.0709,
0.3321,	0.526,	0.7612,
0.0652,	0.3053,	0.44]

#print(a)
a = np.array(input).reshape(-1, 3)/11/1.005/1.2*3600
#plt.plot(a)
#plt.show()
a1 = a[0]
print(sum(a1), a1)
all_balanced(inv_f, inv_s, v1, v2, v3, ve, vm, vf)
print(duct_supply_air.g, duct_1.g, duct_2.g, duct_3.g)

output = []
output2 = []
for i in range(50):
    print(i)
    v1 += (-a1[0] + duct_1.g)/100
    v1 = max(min(v1, 60), 0)
    v2 += (-a1[1] + duct_2.g)/100
    v2 = max(min(v2, 60), 0)
    v3 += (-a1[2] + duct_3.g)/100
    v3 = max(min(v3, 60), 0)
    inv_s += (sum(a1) - duct_supply_air.g)/500
    inv_s = max(min(inv_s, 50), 20)
    inv_f += (sum(a1) - 20 - duct_return_air.g)/500
    inv_f = max(min(inv_f, 50), 20)
    print(v1, v2, v3, inv_s, inv_f)
    output.append([v1, v2, v3, inv_s, inv_f])

    all_balanced(inv_f, inv_s, v1, v2, v3, ve, vm, vf)
    print(duct_supply_air.g, duct_1.g, duct_2.g, duct_3.g)
    output2.append([duct_supply_air.g, duct_1.g, duct_2.g, duct_3.g])

output = np.array(output).reshape(-1, 5)
output2 = np.array(output2).reshape(-1, 4)/100
plt.plot(output)
plt.plot(output2)
plt.show()


#duct_1.g =


