# -*- coding: utf-8 -*-
import numpy as np
import readcsv
import sun_class
import indoor_load_class_900_aircon  # indoor_load_class

# 气象
wea = readcsv.WeatherData("input_data/DRYCOLD01.csv")
# 城市
city = sun_class.Cities('tokyo', 35.68, 139.77, 9)
city2 = sun_class.Cities('USCO', 39.8, -104.9, -6)
# 日照
sun = sun_class.Sun(city2)  ###这句要省略
### 城市和气象和基础设定全部放到building里

## 房间1
# 墙


