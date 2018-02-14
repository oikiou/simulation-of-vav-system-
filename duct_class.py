# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve


# 风阀类
class Damper(object):
    '''风阀'''
    def __init__(self, room, d, rho=1.2):
        self.room = room
        self.d = d
        self.rho = rho
        self.theta = 0
        self.l, self.zeta, self.s = self.theta2para(self.theta)

    def theta2para(self, theta):
        l = 1 - np.sin(np.deg2rad(theta))
        zeta = ((1 - l) * (1.5 - l) / l ** 2)
        s = (8 * self.rho * zeta) / (np.pi ** 2 * self.d ** 4)
        return l, zeta, s

    def theta2s(self, theta):
        l, zeta, s = self.theta2para(theta)
        return s

    def plot(self):
        x = np.linspace(0.01, 89.9)
        l, zeta, s = [[self.theta2s(xi)[i] for xi in x] for i in range(3)]
        plt.plot(x, np.array(l) * 100, label=u"l/l_max")
        plt.plot(x, np.log(zeta), label=u'ln(zeta)')
        plt.plot(x, np.log(s), label=u'ln(s)')
        plt.legend()
        plt.grid(True)
        plt.show()

# 测试
'''
vav1 = Damper('room_1', 0.4)
# vav1.plot()
print(vav1.theta2para(30))
print(vav1.theta2s(30))
'''
vav1 = Damper('room_1', 0.4)
vav2 = Damper('room_2', 0.35)
vav3 = Damper('room_3', 0.45)
fresh_air_damper = Damper('AHU', 0.7)
exhaust_air_damper = Damper('AHU', 0.7)
mix_air_damper = Damper('AHU', 0.7)


# 风管类
# 输入 流量，管长，局部阻力系数
# 输出 管径，流速，S，压力损失
class Duct(object):
    def __init__(self, g, l, xi, d=0., a=0., b=0., v=4., show=False):
        self.g = g  # m3/h  # 流量
        self.l = l  # m  # 管长
        self.xi = xi  # 局部阻力系数
        self.d = d  # 直径(当量直径 d = 2ab/(a+b))
        self.a = a  # 一边(方管可以指定一边)
        self.b = b  # 另一边
        self.v = v  # 流速
        self.A = self.g / 3600 / self.v  # 截面积

        # 公称直径
        nominal_diameter = [0.015, 0.02, 0.025, 0.032, 0.04, 0.05, 0.065, 0.08, 0.1, 0.125, 0.15, 0.2, 0.25,
                            0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8]

        # 圆管
        if self.d == 0:
            self.d_target = (self.A / np.pi) ** 0.5 * 2
            dis = [abs(nd - self.d_target) for nd in nominal_diameter]
            self.d = nominal_diameter[dis.index(min(dis))]

        # 方管
        if self.a != 0 and self.b == 0:
            self.d_target = (self.A / np.pi) ** 0.5 * 2
            self.b_target = self.d_target * self.a / (2 * self.a - self.d_target)
            dis = [abs(nd - self.b_target) for nd in nominal_diameter]
            self.b = nominal_diameter[dis.index(min(dis))]

        if self.a != 0:
            self.d = (2 * self.a * self.b) / (self.a + self.b)  # 当量直径

        # 反推
        self.A = 3.1415 * self.d ** 2 / 4
        self.v = self.g / 3600 / self.A

        # 阻力系数
        self.S = (0.02 * self.l / self.d + self.xi) * 8 * 1.2 / (3.1415 ** 2) / (self.d ** 4)
        # 额定压损
        self.p = self.S * (self.g / 3600) ** 2

        # 打印
        if show:
            if self.a:
                print('a, b, v, S, p')
                print(self.a, self.b, self.v, self.S, self.p)
            else:
                print('d, v, S, p')
                print(self.d, self.v, self.S, self.p)

# 测试
'''
d2 = Duct(1547, 0, 2)
print(d2.d)
d5 = Duct(1547, 0, 2, a=0.5, s_print=True)
'''

theta0 = 0  # 阀门全开
# 送风管段
duct_1 = Duct(1547, 10, 0.05+0.1+0.23+0.4+0.9+1.2+0.23 + vav1.theta2s(theta0), show=True)
duct_2 = Duct(1140, 2.5, 0.3+0.1+0.4+0.23+1.2+0.9 + vav2.theta2s(theta0), show=True)
duct_12 = Duct(1547 + 1140, 7.5, 0.05+0.1, a=0.5, show=True)
duct_3 = Duct(1872, 2.5, 0.3+0.1+0.4+0.23+1.2+0.9 + vav3.theta2s(theta0), show=True)
duct_123 = Duct(1547 + 1140 + 1872, 4.3, 3.6+0.23, a=0.5, show=True)
# 回风管段
duct_return_air = Duct(4342, 1.75, 0.5+0.24, a=0.6, show=True)
duct_exhaust_air = Duct(4342, 0.95, 3.7+0.9+0.4+0.05+exhaust_air_damper.theta2s(theta0), a=0.6, show=True)
duct_fresh_air = Duct(4342, 0.78, 1.4+0.1+0.4+fresh_air_damper.theta2s(theta0), a=0.6, show=True)
duct_mix_air = Duct(4342, 2.2, 0.3+0.4+1.5+mix_air_damper.theta2s(theta0), a=0.6, show=True)


# 水泵 风机
# 性能曲线拟合
class Poly(object):
    """多项式拟合 y是x的多项式 输出k是拟合好的系数"""
    def __init__(self, x, y, dim):
        self.x = np.array(x, dtype=float)
        self.y = np.array(y, dtype=float)
        self.dim = dim
        # please make sure len(self.x) == len(self.y)

        self.dim_ = True  # 是否能满足dim
        if len(self.x) < self.dim + 1:
            self.dim = len(self.x) - 1
            self.dim_ = False

        # 求x的多项式矩阵
        self.x_mat = np.mat([np.power(self.x, i) for i in range(self.dim + 1)]).T

        # 求解
        if len(self.x) == self.dim + 1:  # 精确解
            self.k = self.x_mat.I * np.mat(self.y).T
        elif len(self.x) > self.dim + 1:  # 最优解
            self.k = (self.x_mat.T * self.x_mat).I * self.x_mat.T * np.mat(self.y).T

        # 预测
        self.prediction = self.x_mat * self.k

    def plot(self):
        plt.scatter(self.x, self.y)
        plot_x = np.linspace(self.x.min(), self.x.max())
        plot_x_mat = np.mat([np.power(plot_x, i) for i in range(self.dim + 1)]).T
        plot_y = plot_x_mat * self.k
        plt.plot(plot_x, plot_y)
        plt.show()

# 测试
'''
x = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]
y = [443, 383, 348, 305, 277, 249, 216, 172, 112, 30]
p = Poly(x, y, 3)
print(p.prediction)
p.plot()
'''


class Fan(object):
    """风机特性曲线 x是风量 z是频率 y是不同频率和风量下的压力"""
    def __init__(self, x, y, z, dim1=3, dim2=5):
        self.x = x
        self.y = y
        self.z = z
        self.dim1 = dim1
        self.dim2 = dim2

        # 对不同频率下的风量和压力拟合，求出曲线的系数
        self.h1 = [Poly(self.x[0:len(yi)], yi, self.dim1) for yi in self.y]
        self.k1 = np.array([hi.k for hi in self.h1]).reshape(-1, dim1 + 1)

        # 对不同频率下的曲线的系数拟合
        self.h2 = [Poly(self.z, k1i, dim2) for k1i in self.k1.T]
        self.k2 = np.array([hi.k for hi in self.h2]).reshape(-1, dim2 + 1)

        # check_k1
        self.k1_prediction = np.array([h2i.prediction for h2i in self.h2]).T.reshape(-1, dim1 + 1)
        # k1精度校核

        # check_y
        self.prediction = [np.array(self.k1_prediction[i] * self.h1[i].x_mat.T).flatten() for i in range(len(self.h1))]
        # y精度校核

    # 绘图
    def plot(self):
        for i in range(len(self.h1)):
            plt.scatter(self.h1[i].x, self.h1[i].y)
            plt.plot(self.h1[i].x, self.prediction[i])
        plt.grid(True)
        plt.show()

    # 预测(应用)
    def p(self, g0, inv0):
        g0 = np.array(g0, dtype=float)
        inv0 = np.array(inv0, dtype=float)

        inv_mat = np.mat([np.power(inv0, i) for i in range(self.dim2 + 1)])
        k1_prediction = inv_mat * self.k2.T
        g_mat = np.mat([np.power(g0, i) for i in range(self.dim1 + 1)])

        return np.array(k1_prediction * g_mat.T).flatten()

# 测试
g = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]
p = []
p.append([443, 383, 348, 305, 277, 249, 216, 172, 112, 30])
p.append([355, 296, 256, 238, 207, 182, 148, 97, 21])
p.append([342, 284, 246, 217, 190, 161, 121, 62])
p.append([336, 278, 236, 206, 178, 145, 97, 38])
p.append([320, 264, 223, 189, 153, 109, 50])
p.append([300, 239, 194, 153, 110, 55])
p.append([260, 200, 152, 107, 52])
p.append([179, 129, 79, 24])
inv = [50, 45, 40, 35, 30, 25, 20, 15]
'''
f = Fan(g, p, inv)
print(f.k1)
print(f.k1_prediction)
print(f.prediction)
f.plot()
print(f.p(600, 40))
'''

g1 = list(map(lambda x: x * 4342 / 1200, g))
p1 = [[x * 270 / 216 for x in pi] for pi in p]
#print(p1)
f2 = Fan(g1, p1, inv)
#print(f.k1)
#print(f.k1_prediction)
#print(f.prediction)
#print(f.p(2000, 50))
#f2.plot()
'''
# 理想风机特性曲线
f1_x = f2.h1[0].x
f1_y = f2.h1[0].y
for i in range(8):
    hz = 50 - 5 * i
    x = f1_x * hz / 50
    y = f1_y * (hz / 50) ** 2
    plt.plot(x, y)
    plt.scatter(x, y)
plt.grid(True)
plt.show()
'''
g2 = list(map(lambda x: x * 4342 / 1200, g))
p2 = [[x * 35 / 216 for x in pi] for pi in p]
f1 = Fan(g2, p2, inv)
#f1.plot()


# 排风新风混风段 及 整个风管系统的物理模型
class SupplyAirDuct(object):
    '''送风管路'''
    def __init__(self):
        pass

class supply_fan(Fan):
    def __init__(self, **a):
        super().__init__(**a)

class duct_system(object):
    def __init__(self, terminal, ):
        pass



x = np.linspace(0, 5000)


def f(x):
    x1 = float(x[0])
    x2 = float(x[1])
    x3 = float(x[2])
    return np.array([
        f1.p(x1, 50) - 3.2 * (x1/3600) ** 2 - 20.6 * ((x1 - x3)/3600) ** 2,
        f2.p(x2, 50) - 34.6 * (x2/3600) ** 2 - 10.6 * ((x2 - x3)/3600) ** 2 - 200,
        f1.p(x1, 50) - 3.2 * (x1/3600) ** 2 - 9.1 * (x3/3600) ** 2 - 34.6 * (x2/3600) ** 2 + f2.p(x2, 50) - 200
    ]).flatten()

result = fsolve(f, np.array([1, 1, 1]))

#print(result)
#print(f(result))

# check
g1 = result[0]
g2 = result[1]
p1 = (f1.p(g1, 50))
p2 = (f2.p(g2, 50))
ub = p1 - 3.2 * (g1/3600) ** 2
ua = p2 - 34.6 * (g2/3600) ** 2 - 200
g31 = g1/3600 - (ub/20.6) ** 0.5
g32 = g2/3600 - (ua/10.6) ** 0.5
g33 = ((ub + ua)/9.1) ** 0.5  # 是加不是减

# print(g1/3600, g2/3600, p1, p2, ub, -ua, g31*3600, g32*3600, g33*3600)


