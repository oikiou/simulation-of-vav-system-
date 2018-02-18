# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve


# 风阀类
class Damper(object):
    def __init__(self, d, rho=1.2, theta0=0):
        self.d = d  # 管径(m)
        self.rho = rho  # 空气密度ρ(kg/m3)
        self.theta = theta0  # 开度θ（角度，0-90，默认0，既全开）
        self.l = 1  # 开度(百分比，0-1，默认1，全开)
        self.zeta = 0  # ζ，局部阻力系数
        self.s = 0  # p = SG2 的 S
        self.theta_run(self.theta)  # 初始化l, ζ，S

    def theta_run(self, theta):
        # θ确定的情况下，算l, ζ，S
        self.theta = theta
        self.l = 1 - np.sin(np.deg2rad(self.theta))
        self.zeta = ((1 - self.l) * (1.5 - self.l) / self.l ** 2)
        self.s = (8 * self.rho * self.zeta) / (np.pi ** 2 * self.d ** 4)

    def plot(self):
        # 绘图 阀门特性曲线
        theta00 = self.theta
        x = np.linspace(0.01, 89.9)
        l = []
        zeta = []
        s = []
        for xi in x:
            self.theta_run(xi)
            l.append(self.l)
            zeta.append(self.zeta)
            s.append(self.s)
        plt.plot(x, np.array(l) * 100, label=u"l/l_max")
        plt.plot(x, np.log(zeta), label=u'ln(zeta)')
        plt.plot(x, np.log(s), label=u'ln(s)')
        plt.legend()
        plt.grid(True)
        plt.show()
        self.theta_run(theta00)

# 测试
'''
vav1 = Damper(0.4)
# vav1.plot()
print(vav1.theta2para(30))
print(vav1.theta2s(30))
'''
# 三个房间的VAV风阀 和 空调箱的三个风阀
vav1 = Damper(0.35)
vav2 = Damper(0.3)
vav3 = Damper(0.4)
fresh_air_damper = Damper(0.6)
exhaust_air_damper = Damper(0.6)
mix_air_damper = Damper(0.6)


# 风管类
class Duct(object):
    # 输入 流量，管长，局部阻力系数
    # 输出 管径，流速，S，压力损失
    def __init__(self, g, l, zeta, d=0., a=0., b=0., v=4., damper=None, show=False):
        self.g = g  # m3/h  # 流量
        self.l = l  # m  # 管长
        self.zeta = zeta  # 局部阻力系数ζ
        self.d = d  # 直径(当量直径 d = 2ab/(a+b))
        self.a = a  # 一边(方管可以指定一边)
        self.b = b  # 另一边
        self.v = v  # 流速
        self.damper = damper  # 管路中的可调部件，为了传递s
        self.A = self.g / 3600 / self.v  # 截面积
        self.s = 0

        # 管路树结构中的叶子节点
        self.left = None
        self.right = None
        self.root = 'duct'

        # 公称直径库
        nominal_diameter = [0.015, 0.02, 0.025, 0.032, 0.04, 0.05, 0.065, 0.08, 0.1, 0.125, 0.15, 0.2, 0.25,
                            0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8]

        # 圆管
        if self.d == 0:  # 不指定管径
            self.d_target = (self.A / np.pi) ** 0.5 * 2  # 目标直径
            dis = [abs(nd - self.d_target) for nd in nominal_diameter]  # 残差
            self.d = nominal_diameter[dis.index(min(dis))]  # 选定管径

        # 方管
        if self.a != 0 and self.b == 0:  # 指定一条边
            self.d_target = (self.A / np.pi) ** 0.5 * 2  # 目标直径
            self.b_target = self.d_target * self.a / (2 * self.a - self.d_target)  # 湿周 计算零一条边的目标值
            dis = [abs(nd - self.b_target) for nd in nominal_diameter]  # 残差
            self.b = nominal_diameter[dis.index(min(dis))]  # 选定另一条边

        if self.a != 0:  # 指定两条边
            self.d = (2 * self.a * self.b) / (self.a + self.b)  # 当量直径

        # 反推
        self.A = 3.1415 * self.d ** 2 / 4
        self.v = self.g / 3600 / self.A

        # 阻力系数
        self.s_cal()
        # 额定压损
        self.p = self.s * (self.g / 3600) ** 2

        # 打印
        if show:
            if self.a:
                print('a, b, v, S, p')
                print(self.a, self.b, self.v, self.s, self.p)
            else:
                print('d, v, S, p')
                print(self.d, self.v, self.s, self.p)

    # 多态
    def g_cal(self, g):
        self.g = g
        self.p = self.s * self.g ** 2

    def s_cal(self):
        if self.damper:
            self.s = (0.02 * self.l / self.d + self.zeta + self.damper.zeta) * 8 * 1.2 / (3.1415 ** 2) / (self.d ** 4)
        else:
            self.s = (0.02 * self.l / self.d + self.zeta) * 8 * 1.2 / (3.1415 ** 2) / (self.d ** 4)


# 测试
'''
d2 = Duct(1547, 0, 2)
print(d2.d)
d5 = Duct(1547, 0, 2, a=0.5, s_print=True)
'''

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
    def __init__(self, x, y, z=(50, 45, 40, 35, 30, 25, 20, 15), dim1=3, dim2=5, ideal=False):
        self.x = x
        self.y = y
        self.z = z
        self.dim1 = dim1
        self.dim2 = dim2
        self.ideal = ideal
        self.g = 0
        self.p = 0
        self.inv = 50


        # 对不同频率下的风量和压力拟合，求出曲线的系数
        if ideal:
            self.x0 = [[xi * zi / 50 for xi in self.x] for zi in self.z]
            self.y0 = [[yi * (zi / 50) ** 2 for yi in self.y] for zi in self.z]
            self.h1 = [Poly(self.x0[i], self.y0[i], self.dim1) for i in range(len(self.x0))]
        else:
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
    def predict(self, g0, inv0):
        g0 = np.array(g0, dtype=float)
        inv0 = np.array(inv0, dtype=float)

        inv_mat = np.mat([np.power(inv0, i) for i in range(self.dim2 + 1)])
        k1_prediction = inv_mat * self.k2.T
        g_mat = np.mat([np.power(g0, i) for i in range(self.dim1 + 1)])

        return np.array(k1_prediction * g_mat.T).flatten()


# 测试
g = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]
p = [[443, 383, 348, 305, 277, 249, 216, 172, 112, 30]]
p.append([355, 296, 256, 238, 207, 182, 148, 97, 21])
p.append([342, 284, 246, 217, 190, 161, 121, 62])
p.append([336, 278, 236, 206, 178, 145, 97, 38])
p.append([320, 264, 223, 189, 153, 109, 50])
p.append([300, 239, 194, 153, 110, 55])
p.append([260, 200, 152, 107, 52])
p.append([179, 129, 79, 24])
'''
f = Fan(g, p)
print(f.k1)
print(f.k1_prediction)
print(f.prediction)
f.plot()
print(f.predict(600, 40))
f3 = Fan(g, p[0], ideal=True)
f3.plot()
'''
# 送回风机
g1 = list(map(lambda x: x * 4342 / 1200, g))
p1 = [[x * 70 / 216 for x in pi] for pi in p]
f1 = Fan(g1, p1)  # 回风机
g2 = list(map(lambda x: x * 4342 / 1200, g))
p2 = [[x * 320 / 216 for x in pi] for pi in p]
f2 = Fan(g2, p2)  # 送风机
# f1.plot()


# 风管的树结构
class Branch(object):
    # 支管
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.g = 0
        self.p = 0
        self.s = 0

        # 空枝
        if 'root' not in dir(self):
            self.root = None

        # 计算s
        self.s_cal()

    def s_cal(self):
        # 由上而下的堆栈，由下而上的递归
        self.left.s_cal()
        self.right.s_cal()
        if self.root == 'serial':
            self.s = self.left.s + self.right.s
        elif self.root == 'parallel':
            self.s = self.left.s * self.right.s / (self.left.s ** 0.5 + self.right.s ** 0.5) ** 2
        else:
            raise ValueError

    def g_cal(self, g):
        # 由上而下的递归
        self.g = g
        self.p = self.s * self.g ** 2
        if self.root == 'serial':
            self.left.g_cal(self.g)
            self.right.g_cal(self.g)
        elif self.root == 'parallel':
            self.left.g_cal(self.g * (self.s / self.left.s) ** 0.5)
            self.right.g_cal(self.g * (self.s / self.right.s) ** 0.5)


class Parallel(Branch):
    # 并联节点
    def __init__(self, left, right):
        self.root = 'parallel'
        super().__init__(left, right)


class Serial(Branch):
    # 串联节点
    def __init__(self, left, right):
        self.root = 'serial'
        super().__init__(left, right)

# 送风管
duct_supply_air = Serial(duct_123, Parallel(duct_3, Serial(duct_12, Parallel(duct_1, duct_2))))
# print(duct_supply_air.s)
# duct_supply_air.g_cal(4342)
# print(duct_1.g, duct_2.g, duct_3.g)


# 排风新风混风段 及 整个风管系统的物理模型
class DuctSystem(object):
    # 构筑风系统 包括，5段风管，两台风机，一个空调箱，空调箱作为定压源
    def __init__(self, duct_supply_air, duct_return_air, duct_exhaust_air, duct_fresh_air,
                 duct_mix_air, fan_s, fan_r, dp_ahu=200):
        self.duct_supply_air = duct_supply_air
        if isinstance(duct_return_air, Duct):  # 确保类型匹配
            self.duct_return_air = duct_return_air
        else:
            raise TypeError
        self.duct_exhaust_air = duct_exhaust_air
        self.duct_fresh_air = duct_fresh_air
        self.duct_mix_air = duct_mix_air
        if isinstance(fan_s, Fan):
            self.fan_s = fan_s
        else:
            raise TypeError
        self.fan_r = fan_r
        self.dp_ahu = dp_ahu

        self.g_return_air = 0
        self.g_supply_air = 0
        self.g_mix_air = 0

    def balance(self):
        # 管路平衡计算
        print(self.duct_return_air.s, self.duct_exhaust_air.s, self.duct_supply_air.s, self.duct_fresh_air.s, self.duct_mix_air.s)
        print(self.fan_r.predict(4000, self.fan_r.inv), self.fan_s.predict(4000, self.fan_s.inv))

        # 用于scipy.optimize.fsolve解方程
        def f(x):
            x1 = float(x[0])
            x2 = float(x[1])
            x3 = float(x[2])
            return np.array([
                self.fan_r.predict(x1, self.fan_r.inv) - self.duct_return_air.s * (x1 / 3600) ** 2 -
                self.duct_exhaust_air.s * ((x1 - x3) / 3600) ** 2,
                self.fan_s.predict(x2, self.fan_s.inv) - self.duct_supply_air.s * (x2 / 3600) ** 2 -
                self.duct_fresh_air.s * ((x2 - x3) / 3600) ** 2 - self.dp_ahu,
                self.fan_r.predict(x1, self.fan_r.inv) - self.duct_return_air.s * (x1 / 3600) ** 2 -
                self.duct_mix_air.s * (x3 / 3600) ** 2 - self.duct_supply_air.s * (x2 / 3600) ** 2 +
                self.fan_s.predict(x2, self.fan_s.inv) - self.dp_ahu
            ]).flatten()

        [self.g_return_air, self.g_supply_air, self.g_mix_air] = fsolve(f, np.array([1, 1, 1]))
        print(self.g_return_air, self.g_supply_air, self.g_mix_air)

    def balance_check(self):
        # 检查方程的解
        g1 = self.g_return_air
        g2 = self.g_supply_air
        p1 = self.fan_r.predict(g1, self.fan_r.inv)
        p2 = self.fan_s.predict(g2, self.fan_s.inv)
        ub = p1 - self.duct_return_air.s * (g1 / 3600) ** 2
        ua = - (p2 - self.duct_supply_air.s * (g2 / 3600) ** 2 - self.dp_ahu)
        g31 = g1 / 3600 - (ub / self.duct_exhaust_air.s) ** 0.5
        g32 = g2 / 3600 - (- ua / self.duct_fresh_air.s) ** 0.5
        g33 = ((ub - ua)/self.duct_mix_air.s) ** 0.5
        # 检查气流方向是否正确 ua<0, ub>0

        print(g1/3600, g2/3600, p1, p2, ub, ua, g31*3600, g32*3600, g33*3600)

# 风管系统
duct_system = DuctSystem(duct_supply_air, duct_return_air, duct_exhaust_air, duct_fresh_air, duct_mix_air, f2, f1)
f1.inv = f2.inv = 40
duct_system.balance()
duct_system.balance_check()
print(duct_supply_air.s)

f1.inv = 25
f2.inv = 50
vav1.theta_run(40)
vav2.theta_run(40)
vav3.theta_run(40)
fresh_air_damper.theta_run(30)
mix_air_damper.theta_run(5)
exhaust_air_damper.theta_run(35)

print(duct_supply_air.s)
duct_system.balance()
duct_system.balance_check()

duct_supply_air.g_cal(duct_system.g_supply_air)
print(duct_1.g, duct_2.g, duct_3.g)

vav1.theta_run(50)
vav2.theta_run(40)
vav3.theta_run(50)
fresh_air_damper.theta_run(30)
mix_air_damper.theta_run(5)
exhaust_air_damper.theta_run(35)
duct_1.s_cal()
duct_2.s_cal()
duct_3.s_cal()
duct_fresh_air.s_cal()
duct_mix_air.s_cal()
duct_exhaust_air.s_cal()
duct_supply_air.s_cal()
duct_system.balance()
duct_system.balance_check()

duct_supply_air.g_cal(duct_system.g_supply_air)
print(duct_1.g, duct_2.g, duct_3.g)

