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
        self.f_mat = np.mat([np.power(self.x, j) for j in range(self.dim + 1)]).T
        if len(self.x) == self.dim + 1:  # 精确解
            self.k = self.f_mat.I * np.mat(self.y).T
        elif len(self.x) > self.dim + 1:  # 最优解
            self.k = (self.f_mat.T * self.f_mat).I * self.f_mat.T * np.mat(self.y).T
        else:  # 无解 按最大维度求解
            self.dim = len(self.x) - 1
            self.f_mat = np.mat([np.power(self.x, j) for j in range(self.dim + 1)]).T
            self.k = self.f_mat.I * np.mat(self.y).T

    def fan_check(self):
        return self.f_mat * self.k

    def fan_plot(self):
        plt.scatter(self.x, self.y)
        plot_x = np.linspace(self.x.min(), self.x.max())
        plot_y = np.reshape([([np.power(i, j) for j in range(self.dim + 1)] * self.k) for i in plot_x], [1, -1])[0]
        plt.plot(plot_x, plot_y)

x = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]
y = []
y.append([443, 383, 348, 305, 277, 249, 216, 172, 112, 30])
y.append([355, 296, 256, 238, 207, 182, 148, 97, 21])
y.append([342, 284, 246, 217, 190, 161, 121, 62])
y.append([336, 278, 236, 206, 178, 145, 97, 38])
y.append([320, 264, 223, 189, 153, 109, 50])
y.append([300, 239, 194, 153, 110, 55])
y.append([260, 200, 152, 107, 52])
y.append([179, 129, 79, 24])
# y.append([80, 45])
z = [50, 45, 40, 35, 30, 25, 20, 15]

hk = []
h = [Fan([x[0:len(yi)], yi], 3) for yi in y]
for i in range(len(h)):
    # h[i].fan_plot()
    plt.scatter(h[i].x, h[i].y)
    hk.append(h[i].k)
    # print(h[i].x * h[i].y / 1000)
# plt.show()
hk = np.array(hk).reshape(-1,4)
print(hk)
h2 = [Fan([z, hki], 5) for hki in hk.T]
k2 = []
for i in range(len(h2)):
    # print(h2[i].fan_check())
    #h2[i].fan_plot()
    #plt.show()
    k2.append(h2[i].k)
k2 = np.array(k2).reshape(-1,6)
print(k2)

print(np.mat([np.power(50, j) for j in range(5 + 1)]) * k2.T)

for i in range(15,51):
    plot_x = np.linspace(0, 1800)
    i_fat = np.mat([np.power(i, j) for j in range(5 + 1)])
    k = i_fat * k2.T
    plot_y = np.reshape([([np.power(i, j) for j in range(3 + 1)] * k.T) for i in plot_x], [1, -1])[0]
    plt.plot(plot_x, plot_y)

plt.show()
'''
class Poly():
    """多项式拟合"""
    def __init__(self, x, y, dim):
'''
