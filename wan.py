'''
import sys
print('================Python import mode==========================');
print ('命令行参数为:')
for i in sys.argv:
    print (i)
print ('\n python 路径为',sys.path)

a=b=[1,2]
a[1]=0
print(a,b)


a, b, c, d = 20, 5.5, True, 4+3j
print(type(a), type(b), type(c), type(d))
# <class 'int'> <class 'float'> <class 'bool'> <class 'complex'>


a =[[1,2,3,4,5]*2]+[[2,3,4,5,6]*2]
print(a)
print(a[1][1])


import sys


def fibonacci(n):  # 生成器函数 - 斐波那契
    a, b, counter = 0, 1, 0
    while True:
        if (counter > n):
            return
        yield a
        a, b = b, a + b
        counter += 1


f = fibonacci(10)  # f 是一个迭代器，由生成器返回生成

while True:
    try:
        print(next(f), end=" ")
    except StopIteration:
        sys.exit()




import math
print('常量 PI 的值近似为：%0.3f。' % math.pi)


# 类定义
class people:
    # 定义基本属性
    name = ''
    age = 0
    # 定义私有属性,私有属性在类外部无法直接进行访问
    __weight = 0

    # 定义构造方法
    def __init__(self, n, a, w):
        self.name = n
        self.age = a
        self.__weight = w

    def speak(self):
        print("%s 说: 我 %d 岁。" % (self.name, self.age))


# 单继承示例
class student(people):
    grade = ''

    def __init__(self, n, a, w, g):
        # 调用父类的构函
        # people.__init__(self, n, a, w)
        self.grade = g
        super().__init__(n,a,w)

    # 覆写父类的方法
    def speak(self):
        print("%s 说: 我 %d 岁了，我在读 %d 年级" % (self.name, self.age, self.grade))


s = student('ken', 10, 60, 3)
s.speak()


def average(values):
    return sum(values) / len(values)

import doctest
doctest.testmod()
'''

'''
import numpy as np

intth =0.1
tr =1.4
shc =1934
intti =120
ln = 10
tcn = 10
ot = 10
act = 25

Rln = 0.108
R0 = 0.108
# Rcn/R0 = 1/9.3 , 9.3= boundary thermal resistance
R = intth / tr

CAPln = 0
CAP0 = 0
# CAP0/5 = CAP boundary condition
CAP = shc * intth * 1000
CAP_ = CAP

uL0 = intti / (0.5 * (CAP0 + CAP) * R0)
uR0 = intti / (0.5 * (CAP0+CAP)*R)

# uL0 uR0 = Starting position: boundary condition

uLln = intti / (0.5*(CAPln + CAP) * R)
uRln = intti / (0.5*(CAPln + CAP) * Rln)

# uL0 uR0 = Ending position: boundary condition

uL = intti / (CAP * R)
uR = intti / (CAP * R)

T = np.ones((ln+1, tcn+1))*10

# j = time step
# i = thickness step
for j in range(1, tcn+1):
    if j == 0:
        for i in range(ln+1):
            if i == 0:
                T[j][i] = uL0*act + (1-uL0-uR0)*ot + uR0*ot
            elif i == ln:
                T[j][i] = uLln*ot + (1-uLln-uRln)*ot + uRln*ot
            else:
                T[j][i] = uL*ot + (1-uL-uR)*ot+uR0*ot
    else:
        for i in range(ln+1):
            if i == 0:
                T[j][i] = uL0*act + (1-uL0-uR0)*T[j-1][i] + uR0*T[j-1][i+1]
            elif i == ln:
                T[j][i] = uLln*T[j-1][i-1] + (1-uLln-uRln)*T[j-1][i] + uRln*ot
            else:
                T[j][i] = uL*T[j-1][i-1] + (1-uL-uR)*T[j-1][i]+uR*T[j-1][i+1]
                pass
    pass
print(np.round(np.array(T), 2))

'''

import numpy as np
import matplotlib.pyplot as plt
import math
np.set_printoptions(formatter={'float': '{: 0.3f}'.format})


d1 = 0.2
n1 = 4
indoor_t1 = 26
outdoor_t1 = -5
time1 = 10080
_lambda1 = 0.179
_c_rho1 = 1624

def diff_m(d, n, indoor_t, outdoor_t, time, _lambda, _c_rho ):

    r_out = [1/23]
    r_n = [d/n/_lambda]
    r_in = [1/9]

    r = r_out + n * r_n + r_in
    print(r)

    cap_out = cap_in = [0]
    cap = cap_out + [_c_rho *1000 * d/n]* n + cap_in

    print(cap)

    t = [0.5 * (cap[i]+cap[i+1])/((1/r[i]) + 1/r[i+1]) for i in range(n+1)]

    print(t)

    dt = math.floor(  min(t))
    print(dt)

    dt = 100

    ul = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i] for i in range(n+1)];

    print(ul)

    ur = [dt / 0.5 / (cap[i] + cap[i + 1]) / r[i + 1] for i in range(n+1)]
    print(ur)

    un = np.multiply(np.add(ul, ur), -1) +1
    print(un)

    t_out = []

    t_old_n = [0] * (n+1)  # 初始条件
    print(list(t_old_n[1:]) + [outdoor_t])

    print(ul)
    print([indoor_t] + list(t_old_n[:-1]))
    for i in range(int(time / dt)):

        t_old_r = [indoor_t] + list(t_old_n[:-1])

        t_old_l = list(t_old_n[1:]) + [outdoor_t]

        t_new = np.multiply(ul, t_old_l) + np.multiply(un, t_old_n) + np.multiply(ur, t_old_r)

        t_out.extend(list(t_new))

        t_old_n = t_new

    print(np.array(t_out).reshape(-1, n+1))

    plt.plot(np.array(t_out).reshape(-1, n+1))

    plt.show()

diff_m(d1,n1,indoor_t1,outdoor_t1,time1,_lambda1,_c_rho1)


