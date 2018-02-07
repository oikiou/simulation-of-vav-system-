# 风管类
# 输入 流量，管长，局部阻力系数
# 输出 选择的管径，流速，S，压力损失
class Duct(object):
    def __init__(self, G, L, kexi, r=0, v=4, style='round'):
        self.G = G  # m3/h
        self.L = L  # m
        self.kexi = kexi
        self.r = r
        self.v = v
        self.style = style
        self.A = self.G / 3600 / self.v

        # 管径
        round_d = [0.015, 0.02, 0.025, 0.032, 0.04, 0.04, 0.07, 0.08, 0.1, 0.125, 0.15, 0.2, 0.25, 0.3, 0.35,
                   0.4, 0.45, 0.5, 0.6, 0.7, 0.8]
        round_r = [x / 2 for x in round_d]
        if self.style is 'round' and self.r == 0:
            for r in round_r:
                if 3.1415 * (r ** 2) > self.A:
                    self.r = r
                    break

        # 反推
        self.A = 3.1415 * self.r ** 2
        self.v = self.G / 3600 / self.A
        self.d = self.r * 2
        self.S = (0.02 * self.L / self.d + self.kexi) * 8 * 1.2 / (3.1415 ** 2) / (self.d ** 4)

        self.p = self.S * (self.G / 3600) ** 2

d1 = Duct(4342, 0.78, 2.6)
#print(d1.r, d1.v, d1.S, d1.p)
#print((4342/3600)**2*19.7)


# 水泵 风机
# 性能曲线拟合
import numpy as np
import matplotlib.pyplot as plt


class Fan(object):
    def __init__(self, perf, dim):  # 性能曲线矩阵[x[], y[]]，曲线拟合次数
        self.x = np.array(perf[0], dtype=float)
        self.y = np.array(perf[1], dtype=float)
        self.dim = dim
        self.f_mat = np.mat([np.power(self.x, j) for j in range(dim + 1)]).T
        if len(self.x) == self.dim + 1:  # 精确解
            self.k = self.f_mat.I * np.mat(self.y).T
        else:  # 近似解
            self.k = (self.f_mat.T * self.f_mat).I * self.f_mat * self.y.T

    def fan_check(self):
        return self.f_mat * self.k

    def fan_plot(self):
        plot_x = np.linspace(0, self.x[-1])
        plot_y = np.reshape([([np.power(i, j) for j in range(self.dim + 1)] * self.k) for i in plot_x], [1, -1])[0]
        plt.plot(plot_x, plot_y)
        plt.show()

a = Fan([[0, 440, 1160, 1860], [443, 330, 240, 0]], 3)
print(a.fan_check())
a.fan_plot()
