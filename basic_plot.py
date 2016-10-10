# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-50.0, 50.0, 500)
y = np.sin(x)/x

plt.plot(x,y,'g.') 
