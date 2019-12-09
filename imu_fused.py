import pexpect
import time
import math
import os
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys


last_read_time = 0.0
last_x_angle = 0.0
last_y_angle = 0.0
last_z_angle = 0.0



class IMU_Read:
	
	def __init__(self):
		self.roll = 0
		self.pitch = 0
		self.yaw = 0
		self.roll_list = []
		self.pitch_list = []
		self.yaw_list = []
		self.count = 0
		self.x_axis = []
		self.DEVICE = "00:04:79:00:0d:ca"
		print("eSense address:"),
		print(self.DEVICE)

		# Run gatttool interactively.
		print("Run gatttool...")
		self.child = pexpect.spawn("gatttool -I")

		# Connect to the device.
		print("Connecting to "),
		print(self.DEVICE),
		self.child.sendline("connect {0}".format(self.DEVICE))
		self.child.expect("Connection successful", timeout=5)
		print(" Connected!")

		self.child.sendline("char-read-hnd 0x0c")
		self.child.expect("Characteristic value/descriptor: ", timeout=10)
		self.child.expect("\r\n", timeout=10)
		print("Start/Stop Value: {0} ".format(self.child.before.decode("utf-8")))

		print("Starting the IMU data sampling....")

		self.child.sendline("char-write-req 0x0c 5335020132")
		self.child.expect("Characteristic value was written successfully", timeout=10)
		self.child.expect("\r\n", timeout=10)
		print("Write successful, IMU started publishing")


	def read_values(self):
		self.child.sendline("char-read-hnd 0x000e")
		self.child.expect("Characteristic value/descriptor: ", timeout=10)
		raw = self.child.before.decode("utf-8").split('\r\n')
		try:
			for i in range(1,len(raw)):
				if(len(raw[i]) > 100):
					imu_data = raw[i]
					imu_values = imu_data[76:123]
					_imu_values = imu_values[12:14]
					try:
						gyro_x, gyro_y, gyro_z = self.getGyroValues(imu_values)
						accl_x, accl_y, accl_z = self.getAcclValues(imu_values)

					except:
						continue
	                
					print("\n")
					dt =  1/50

	                # Calculate angle of inclination or tilt for the x and y axes with acquired acceleration vectors
					acc_angle_x, acc_angle_y, acc_angle_z = self.acc_angle(accl_x, accl_y, accl_z)
					gyr_angle_x, gyr_angle_y, gyr_angle_z = self.gyr_angle(gyro_x, gyro_y, gyro_z, dt)
	        
	                # filtered tilt angle
					self.roll, self.pitch, self.yaw = self.c_filtered_angle(acc_angle_x, acc_angle_y, acc_angle_z,  gyr_angle_x, gyr_angle_y, gyr_angle_z)
					print("Roll: {0:.3f}  Pitch: {1:.3f} Yaw: {2:.3f}".format(self.roll, self.pitch, self.yaw))
					self.set_last_read_angles(gyr_angle_x, gyr_angle_y, gyr_angle_z)
					self.roll_list.append(self.roll)
					self.pitch_list.append(self.pitch)
					self.yaw_list.append(self.yaw)
					self.x_axis.append(self.count)
					self.count+=1
	                #f.write("{0:.3f}, {1:.3f}, {2:.3f} \n".format(roll, pitch, yaw))
	                 
		
		except pexpect.exceptions.TIMEOUT:
			pass

		return self.roll_list, self.pitch_list, self.yaw_list, self.x_axis


	def hexStrToInt(self, hexstr1, hexstr2):
	    val = int(hexstr2,16) + (int(hexstr1,16)<<8)
	    if ((val&0x8000)==0x8000): # treat signed 16bits
	        val = -((val^0xffff)+1)
	    return val


	def getGyroValues(self, hexstr):
	    gyro_x = self.hexStrToInt(hexstr[12:14], hexstr[15:17])/65.5
	    gyro_y = self.hexStrToInt(hexstr[18:20], hexstr[21:23])/65.5
	    gyro_z = self.hexStrToInt(hexstr[24:26], hexstr[27:29])/65.5

	    return gyro_x, gyro_y, gyro_z


	def getAcclValues(self, hexstr):
	    accl_x = (self.hexStrToInt(hexstr[30:32], hexstr[33:35])/8192)*9.80665
	    accl_y = (self.hexStrToInt(hexstr[36:38], hexstr[39:41])/8192)*9.80665
	    accl_z = (self.hexStrToInt(hexstr[42:44], hexstr[45:47])/8192)*9.80665

	    return accl_x, accl_y, accl_z


	def c_filtered_angle(self, ax_angle, ay_angle, az_angle, gx_angle, gy_angle, gz_angle):
	    alpha = 0.98
	    
	    pitch = alpha*gx_angle + (1.0 - alpha)*ax_angle
	    
	    yaw = alpha*gy_angle + (1.0 - alpha)*ay_angle
	    
	    roll = alpha*gz_angle + (1.0 - alpha)*az_angle

	    # c_angle_x = alpha*gx_angle + (1.0 - alpha)*ax_angle
	    # c_angle_y = alpha*gy_angle + (1.0 - alpha)*ay_angle
	    # c_angle_z = alpha*gz_angle + (1.0 - alpha)*az_angle
	    return roll, pitch, yaw


	def get_last_x_angle(self):
	    return last_x_angle

	def get_last_y_angle(self):
	    return last_y_angle

	def get_last_z_angle(self):
	    return last_z_angle

	def gyr_angle(self, Gx, Gy, Gz, dt):
	    gx_angle = Gx*dt + self.get_last_x_angle()
	    gy_angle = Gy*dt + self.get_last_y_angle()
	    gz_angle = Gz*dt + self.get_last_z_angle()
	    return gx_angle, gy_angle, gz_angle

	def acc_angle(self, Ax, Ay, Az):
	    radToDeg = 180/3.14159
	    ax_angle = math.atan(Ax/(math.sqrt(math.pow(Ay,2) + math.pow(Az, 2))+ 0.00001))*radToDeg       
	    ay_angle = math.atan((-Ay)/(math.sqrt(math.pow(Ay,2) + math.pow(Az, 2))+ 0.00001))*radToDeg  
	    az_angle = math.atan((-Az)/(math.sqrt(math.pow(Ax,2) + math.pow(Ax,2)) + 0.00001))*radToDeg   
	    return ax_angle, ay_angle, az_angle

	def set_last_read_angles(self, x, y, z):
	    global last_x_angle, last_y_angle, last_z_angle
	    last_x_angle = x
	    last_y_angle = y
	    last_z_angle = z



class Plot2D():
    def __init__(self):
        self.traces = dict()

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title="Attitude Estimation")
        self.win.resize(1000,600)
        self.win.setWindowTitle('IMU Reading : Yaw')
        pg.setConfigOptions(antialias=True)
        self.canvas = self.win.addPlot(title="Yaw")
        self.file = open("Sensor_Data.txt", "r")
        self.i = 0
        self.yaw_list = []
        self.x_list = []
        self.imu_read = IMU_Read()
        

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def trace(self,name,dataset_x,dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x,dataset_y)
        else:
            self.traces[name] = self.canvas.plot(pen='y')
    
    def update(self):
    	roll_list, pitch_list, yaw_list, x_axis = self.imu_read.read_values()
 
    	self.trace("yaw", x_axis, yaw_list)

        #self.trace("cos", self.t, c)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()



if __name__ == '__main__':

    p = Plot2D()
    p.animation()





