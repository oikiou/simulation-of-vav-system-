# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# 读取文件目录
path = 'pandas_input/t'
files = os.listdir(path)
files = ['pandas_input/t/' + file for file in files]

# 设置空表
time = []
for day in range(28):
	day += 1
	if day < 10:
		day = '0' + str(day)
	for hour in range(24):
		if hour < 10:
			hour = '0' + str(hour)
		for minute in range(60):
			if minute < 10:
				minute = '0' + str(min)
			time.append('2018-02-' + str(day) + ' ' + str(hour) + ':' + str(minute))

# data frame zero
dfz = pd.DataFrame({'time': time, 'ch': [np.nan] * len(time)})
dfz = dfz.set_index('time')

for file in files:
	# 跳过开头行 删除无用列
	df = pd.read_csv(file, header=45)
	temp = np.float(df.columns[17])
	df.columns = ['a'] + ['time'] + ['a'] * 15 + ['ch'] + ['a'] * 16
	df = df.drop('a', axis=1)
	df.loc[df.shape[0]+1] = {'time': df.time[0], 'ch': temp}

	# 时间截到分钟
	df.time = df.time.map(lambda s: s[:16])
	df = df.set_index('time')

	# 分组求平均 data frame group
	dfg = df.groupby('time').ch.mean()
	dfg = pd.DataFrame({'ch': dfg}).reset_index()
	dfg.columns = ['time', 'ch']
	dfg = dfg.set_index('time')

	# 填充
	dfz = dfz.combine_first(dfg)

# 填0
dfz = dfz.fillna(0)

# 绘图
dfz.plot()
plt.show()

# 输出
dfz.to_csv('pandas_input/ch15_output.csv')
