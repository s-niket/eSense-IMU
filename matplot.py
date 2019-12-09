# python_live_plot.py

import random
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')

x_values = []
y_values = []

index = count()


def animate(i):
    graph_data = open("Sensor_Data.txt", "r").read()
    lines = graph_data.split('\n')

    for line in lines:
        if len(line)>1:
            roll, pitch, yaw = line.split(',')
            x_values.append(next(index))
            y_values.append(random.randint(0, 5))
            plt.cla()
            plt.plot(x_values, y_values)


ani = FuncAnimation(plt.gcf(), animate, 1)


plt.tight_layout()
plt.show()
