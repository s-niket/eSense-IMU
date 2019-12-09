from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import collections
import random
import time
import math
import numpy as np

class DynamicPlotter():

    def __init__(self, sampleinterval=0.01, timewindow=10., size=(600,350)):
        # Data stuff
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Attitude Estimation (Yaw)')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'anlge', 'degrees')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255,0,0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)
        # File Reading
        self.file_data = open("Sensor_Data.txt", "r").read()
        self.lines = self.file_data.split('\n')

    def getdata(self):
        for line in self.lines:
            if len(line)>1:
                try:
                    roll, pitch, yaw = line.split(',')
                    print(yaw)
                except:
                    pass
        return yaw

    def updateplot(self):
        self.databuffer.append( self.getdata() )
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        self.app.processEvents()

    def run(self):
        self.app.exec_()

if __name__ == '__main__':

    m = DynamicPlotter(sampleinterval=0.05, timewindow=10.)
    m.run()
