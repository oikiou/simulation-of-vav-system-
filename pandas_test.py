# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#
# Read_csv
#

df = pd.read_csv('pandas_input/ut1_201708.csv')
# print(df.head(5))
# print(df.describe())
df.columns = ['time', 'flow', 'out_temp', 't_in', 't_out', 'num', 'electric']
# print(df.describe())
# df.plot()
# df.plot(x='time', y=['t_in', 't_out'])

#
# Series Add
#

df['delta_t'] = df.t_in - df.t_out
df['load'] = 4.2 * df.flow * 1000 * df.delta_t / 12 / 3600  # kwh
df['cop'] = df.load / df.electric
# print(df.describe())
# df.delta_t.plot()
# df.delta_t.hist()
# print(df[df.delta_t <= 0])
df['percentage'] = df.load / df.num * 12 / 100
# print(df.percentage.describe())

#
# drop or Nan by replace
#

df = df[(df.delta_t > 0) & (df.cop < 13) & (df.percentage < 1.5)]
# print(df.describe())
# df.cop.hist()
# df.plot(x='time', y=['cop', 'out_temp'])
# df.plot(kind='scatter', x='out_temp', y='cop')
# df.plot(kind='scatter', x='percentage', y='cop')

#
# sort
#

df = df.sort_values('electric')
# print(df.head(5))
df = df.sort_index()

#
# group
#

# group by out_temp
df['out_temp_bin'] = np.round(df.out_temp / 2) * 2
# df.plot(y=['out_temp', 'out_temp_bin'])
# color_bw_bin = list(((df.out_temp_bin - df.out_temp_bin.min()) / (df.out_temp_bin.max() - df.out_temp_bin.min())).astype(str))
color_bw = list(((df.out_temp - df.out_temp.min()) / (df.out_temp.max() - df.out_temp.min())).astype(str))
df.plot(kind='scatter', x='percentage', y='cop', color=color_bw)

# df_g = df.groupby('out_temp_bin')
# print(df_g.cop.mean())
# df_g.cop.mean().plot(color='r')

# group by percentage
# df['percentage_bin'] = np.round(df.percentage / 0.05) * 0.05
# df_g1 = df.groupby('percentage_bin')
# print(df_g1.cop.mean())
# df_g1.cop.mean().plot(color='r')

# double group
# method 1
'''
df_g2 = df.groupby(['out_temp_bin', 'percentage_bin'])
df_g2_cop_mean = df_g2.cop.mean().reset_index().pivot(index='percentage_bin', columns='out_temp_bin', values='cop')
df_g2_cop_mean.plot(color=[str(i) for i in np.linspace(0.1, 0.9, 9)])
'''

# method 2
'''
for t in np.linspace(20, 36, 9):
	df_t = df[df.out_temp_bin == t]
	print(df[df.out_temp_bin == t].groupby(by='percentage_bin').cop.mean())
	df[df.out_temp_bin == t].groupby(by='percentage_bin').cop.mean().plot(color=str((37-t)/16))
'''

plt.show()












