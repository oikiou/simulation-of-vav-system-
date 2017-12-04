# !/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import load_window

[gt,ga,go] = load_window.load_window(26, 112.5, 3.6)
# n = 5922
# print(gt[n],ga[n],go[n])

plt.plot(gt)
plt.plot(ga)
plt.plot(go)
plt.show()

