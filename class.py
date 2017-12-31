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

'''

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


# getattr



