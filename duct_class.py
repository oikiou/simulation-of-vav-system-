class Duct(object):
    def __init__(self, G, L, kexi, r=0, v=4, style='round'):
        self.G = G  # m3/h
        self.L = L  # m
        self.kexi = kexi
        self.r = r
        self.v = v
        self.style = style
        self.A = self.G / 3600 / self.v
        round_d = [0.015, 0.02, 0.025, 0.032, 0.04, 0.04, 0.07, 0.08, 0.1, 0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                 0.5, 0.6, 0.7, 0.8]
        round_r = [x / 2 for x in round_d]
        if self.style is 'round' and self.r == 0:
            for r in round_r:
                if 3.1415 * (r ** 2) > self.A:
                    self.r = r
                    break
        self.A = 3.1415 * self.r ** 2
        self.v = self.G / 3600 / self.A
        self.d = self.r * 2
        self.S = (0.02 * self.L / self.d + self.kexi) * 8 * 1.2 / (3.1415 ** 2) / (self.d ** 4)

d1 = Duct(1134, 12, 1)
print(d1.r, d1.v, d1.S)