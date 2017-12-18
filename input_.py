# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

# 1.1 壁体
# 透光面  1 窗 - (材料，朝向，面积，透光面积，透光率，吸收日射取得率, 贯流)
face_t = [[["6mm"], 45, 28, 24, 0.79, 0.04, 6.4]]
face_t_n = len(face_t)
# 不透光面  1 外壁  2 内壁  3 床  4 天井 - (类型，材料，厚度，朝向，面积，网格划分数)
face = [[1, ["concrete", "rock_wool", "air", "arumi"], [0.150, 0.050, 0, 0.002], 45, 22.4, [7, 2, 1, 1]]]
face.append([2, ["concrete"], [0.120], 0, 100.8, [6]])
face.append([3, ["carpet", "concrete", "air", "stonebodo"], [0.015, 0.150, 0, 0.012], 0, 98, [1, 7, 1, 1]])
face.append([4, ["stonebodo", "air", "concrete", "carpet"], [0.012, 0, 0.150, 0.015], 0, 98, [1, 1, 7, 1]])
face_n = len(face)

face_t = [[["6mm"], [45, 0], [28, 24], 0.79, 0.04, 6.4]]
face = [[[1, 1], ["concrete", "rock_wool", "air", "arumi"], [0.150, 0.050, 0, 0.002], 45, 22.4, [7, 2, 1, 1]]]

