# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(formatter={'float': '{: 0.3f}'.format})


def diff_m(d, m, dt, indoor_t, outdoor_t, time, _lambda, _c_rho):
    r = [1/9] + [d/m/_lambda] * m + [1/23]
    cap = [0] + [_c_rho*d/m*1000] * m + [0]
    ul = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i] for i in range(m + 1)]
    ur = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i + 1] for i in range(m + 1)]
    um = np.multiply(np.add(ul, ur), -1) + 1
    t_out = []
    t_old_m = [0] * (m + 1)  # 初始条件
    for i in range(int(time / dt)):
        t_old_l = [indoor_t] + list(t_old_m[:-1])
        t_old_r = list(t_old_m[1:]) + [outdoor_t]
        t_new = np.multiply(ul, t_old_l) + np.multiply(um, t_old_m) + np.multiply(ur, t_old_r)
        t_out.extend(list(t_new))
        t_old_m = t_new
    print(np.array(t_out).reshape(-1, m + 1))
    plt.plot(np.array(t_out).reshape(-1, m + 1))
    plt.show()

# 厚度，网格数，时间间隔，室温，外气温度，计算时长，传热系数，质量比热
diff_m(0.2, 3, 60, 26, 0, 3600, 1.4, 1934)
#diff_m(1, 10, 120, 25, 10, 1200, 1.4, 1934)