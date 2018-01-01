# -*- coding: utf-8 -*-
'''
class envelope():
    def __init__(self, a):
        self.area = a

class window(envelope): # 继承类
    def __init__(self, a):


w1 = envelope(40)
print(w1.area)


# test
class Student(object):

    def __init__(self, name, score):
        self.__name = name
        self.__score = score

    def print_score(self):  # 封装
        print(self.__name, self.__score)



bart = Student('Bart Simpson', 59)
lisa = Student('Lisa Simpson', 87)
bart.print_score()
print(lisa, lisa.__score)
bart.a = 1
print(bart.a)


# 继承和多态
class Animal(object):
    def run(self):
        print('Animal is running')

class Dog(Animal):
    def run(self):
        print('Dog is running')

    def eat(self):
        print('Eating meat')

class Cat(Animal):
    def run(self):
        print('Cat is running')

def run_twice(animal):
    animal.run()
    animal.run()

run_twice(Animal())  # Animal()就是animal的一个实例


dog = Dog()
cat = Cat()
dog.run()
cat.run()


# 获取对象信息

print(type(123))
print(isinstance(123, int))


# len调用对象的__len__()方法
class Mydog(object):
    def __len__(self):
        return 123

dog = Mydog()
print(len(dog))
print(dir(dog))



# 类属性 统计
class Student(object):
    count = 0

    def __init__(self, name):
        self.name = name
        Student.count += 1

# 测试
if Student.count != 0:
    print('测试失败1!')
else:
    bart = Student('Bart')
    if Student.count != 1:
        print('测试失败2!')
    else:
        lisa = Student('Bart')
        if Student.count != 2:
            print('测试失败3!')
        else:
            print('Students:', Student.count)
            print('测试通过!')



# slots 限制实例的属性
# raise ValueError
class Student(object):

    def get_score(self):
        return self._score

    def set_score(self, value):
        if not isinstance(value, int):
            raise ValueError('integer!')  # raise了之后就直接中断操作?
        if value < 0 or value > 100:
            raise ValueError('0-100!')
        self._score = value

s = Student()
s.set_score(60)
print(s.get_score())
#s.set_score(9999)
#print(s.get_score())



#  @property 先来一个属性
#  @score.setter 设定这个属性

class Student(object):

    @property  # 把方法变成属性调用  # 本来是s.score(),现在是s.score  # ？property意义何在--在于创建score.setter，可控属性
    def score(self):
        return self._score

    @score.setter  # 赋值语句的方法
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('integer!')  # raise了之后就直接中断操作?
        if value < 0 or value > 100:
            raise ValueError('0-100!')
        self._score = value

s = Student()
s.score = 60
print(s.score)
s.score = 1000


# property 定义只读属性
class Student(object):

    @property
    def birth(self):
        return self._birth

    @birth.setter
    def birth(self, value):
        self._birth = value

    @property
    def age(self):
        return 2018 - self._birth

s = Student()
s.birth = 1994
print(s.age)
# s.age = 24
l = [1,2,3]
# l.__len__ = 4  # __len__ read-only
print(l.__len__())



# 多重继承
# 定制类
# __iter__
class Fib(object):
    def __init__(self):
        self.a ,self.b = 0, 1

    def __iter__(self):
        return self  # 实例本身就是迭代对象??

    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        if self.a > 10000:
            raise StopIteration()
        return self.a

    def __getitem__(self, n):  # 可以按照下标取出元素
        if isinstance(n, int):
            a, b = 0, 1
            for x in range(n):
                a, b = b, a+b
            return a
        if isinstance(n, slice):  # 切片
            start = n.start
            stop = n.stop
            if start is None:
                start = 0
            a, b = 0, 1
            L = []
            for x in range(stop):
                if x >= start:
                    L.append(a)

                a, b = b, a+b
            return L

for n in Fib():
    print(n)
print(Fib()[15])
print(Fib()[3:12])



# call

class Student(object):
    def __init__(self, name):
        self.name = name

    def __call__(self):
        print('My name is %s.' % self.name)

s = Student('Michael')
s()  # 调用实例

print(callable(s))  # 判断一个对象能否被调用，就是看对象内部有没有定义__call__
print(callable([1]))



# 枚举类 # 定义常量 （可以转化成数字编号的常量，像星期，月份等）
from enum import Enum, unique

Month = Enum('Month', ('Jan', 'Feb', 'May'))

for name, member in Month.__members__.items():  # Month.__members__.items()写成Month也是可以的
    print(name, ' ', member, ',', member.value)

print(Month.Jan, Month.Jan.value)
# value 是从1开始的计数

@unique  # 查重
class Weekday(Enum):
    Sun = 0
    Mon = 1
    Tue = 2

day1 = Weekday.Mon


# 练习
from enum import Enum, unique
class Gender(Enum):
    Male = 0
    Female = 1

class Student(object):
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

# 测试
bart = Student('Bart', Gender.Male)
if bart.gender == Gender.Male:
    print('测试通过!')
else:
    print('测试失败!')


# 元类 metaclass

class ListMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['add'] = lambda self, value: self.append(value)
        return  type.__new__(cls, name, bases, attrs)

class Mylist(list, metaclass=ListMetaclass):
    pass

L = Mylist()
L.add(1)
print(L)

# 版本问题？
# ORM 对象-关系映射 框架 底层模块 调用接口



# 偏函数 —— 就是把函数的某些参数固定住的函数
import functools
int2 = functools.partial(int, base=2)
print(int2('1000000'))


# 等同于
def int3(value, base=2):
    return int(value, base)
print(int3('1000000'))



# __doc__ 类的文档字符串
class Employee:
    '所有员工的基类'
    empCount = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.empCount += 1

    def displayCount(self):
        print(Employee.empCount)

    def displayEmployee(self):
        print(self.name, self.salary)

print(Employee.__doc__)  # 类的文档字符串
print(Employee.__dict__)  # 类的字典，所有的属性和值



# 运算符重载

class Vector(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):  # 显示类的时候用
        return 'Vector (%d,%d)' % (self.a, self.b)

    def __add__(self, other):  # 运算符'+'重载
        return Vector(self.a + other.a, self.b + other.b)

v1 = Vector(2,10)
v2 = Vector(5, -2)
print(v1 + v2)



# 私有private

class JustCounter(object):
    __secretCount = 0
    publicCount = 0

    def count(self):
        self.__secretCount += 2
        self.publicCount += 1
        print(self.__secretCount)

counter = JustCounter()
counter.count()
counter.count()
print(counter.publicCount)
#print(counter.__secretCount)

'''

# 计算时间

import time

def sum2(n):
    start = time.time()

    thesum = 0
    for i in range(1,n+1):  # range是可以定开始和结束的
        thesum += i

    end = time.time()

    return thesum, end-start

for i in range(5):
    print('sum is %d required %10.7f seconds'%sum2(1000000))











