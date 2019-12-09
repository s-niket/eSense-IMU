from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from numpy import arange, sin, cos, pi
import pyqtgraph as pg
import sys

class Plot2D():
    def __init__(self):
        self.traces = dict()

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title="Attitude Estimation")
        self.win.resize(1000,600)
        self.win.setWindowTitle('IMU Reading : Yaw')
        pg.setConfigOptions(antialias=True)
        self.canvas = self.win.addPlot(title="IMU")
        self.t = np.arange(0, 10.0, 0.01)
        self.file = open("Sensor_Data.txt", "r")
        self.i = 0
        self.yaw_list = []
        self.x_list = []

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def trace(self,name,dataset_x,dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x,dataset_y)
        else:
            self.traces[name] = self.canvas.plot(pen='y')
    
    def update(self):
        
        lines = self.file.readlines()
        for line in lines:
            roll, pitch, yaw = line.split(',')
            print(yaw)
            self.yaw_list.append(float(yaw))
            self.i+=1
            self.x_list.append(self.i)

        self.trace("Yaw",self.x_list , self.yaw_list)
        s = np.sin(2*np.pi*self.t)
        c = np.cos(2*np.pi*self.t)
        #self.trace("cos", self.t, c)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()


if __name__ == '__main__':

    p = Plot2D()
    p.animation()




