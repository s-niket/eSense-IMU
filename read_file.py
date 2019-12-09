import os
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import style

path = 'Sensor_Data.txt'
#style.use('fivethirtyeight')


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


def animate(i): 
    graph_data = open("Sensor_Data.txt", "r").read()
    lines = graph_data.split('\n')
    ind = 0
    x_axis = []
    roll_list = []
    pitch_list = []
    yaw_list = []

    for line in lines:
        if len(line)>1:
            roll, pitch, yaw = line.split(',')
            print(yaw)
            #plt.scatter(i, yaw)
            #plt.pause(0.00001)
            x_axis.append(ind)
            roll_list.append(roll)
            pitch_list.append(pitch)
            yaw_list.append(yaw)
            ind+=1
    ax1.clear()
    ax1.plot(x_axis, yaw_list)
    #plt.show()


ani = animation.FuncAnimation(fig, animate, frames=30, interval=100)
plt.show()
#f.close
