import pexpect
import time
import math
import os
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from numpy import arange, sin, cos, pi
import pyqtgraph as pg
import sys


last_read_time = 0.0
last_x_angle = 0.0
last_y_angle = 0.0
last_z_angle = 0.0


def hexStrToInt(hexstr1, hexstr2):
    val = int(hexstr2,16) + (int(hexstr1,16)<<8)
    if ((val&0x8000)==0x8000): # treat signed 16bits
        val = -((val^0xffff)+1)
    return val


def getGyroValues(hexstr):
    gyro_x = hexStrToInt(hexstr[12:14], hexstr[15:17])/65.5
    gyro_y = hexStrToInt(hexstr[18:20], hexstr[21:23])/65.5
    gyro_z = hexStrToInt(hexstr[24:26], hexstr[27:29])/65.5

    return gyro_x, gyro_y, gyro_z


def getAcclValues(hexstr):
    accl_x = (hexStrToInt(hexstr[30:32], hexstr[33:35])/8192)*9.80665
    accl_y = (hexStrToInt(hexstr[36:38], hexstr[39:41])/8192)*9.80665
    accl_z = (hexStrToInt(hexstr[42:44], hexstr[45:47])/8192)*9.80665

    return accl_x, accl_y, accl_z




def c_filtered_angle(ax_angle, ay_angle, az_angle, gx_angle, gy_angle, gz_angle):
    alpha = 0.98
    
    pitch = alpha*gx_angle + (1.0 - alpha)*ax_angle
    
    yaw = alpha*gy_angle + (1.0 - alpha)*ay_angle
    
    roll = alpha*gz_angle + (1.0 - alpha)*az_angle

    # c_angle_x = alpha*gx_angle + (1.0 - alpha)*ax_angle
    # c_angle_y = alpha*gy_angle + (1.0 - alpha)*ay_angle
    # c_angle_z = alpha*gz_angle + (1.0 - alpha)*az_angle
    return roll, pitch, yaw


def get_last_x_angle():
    return last_x_angle

def get_last_y_angle():
    return last_y_angle

def get_last_z_angle():
    return last_z_angle

def gyr_angle(Gx, Gy, Gz, dt):
    gx_angle = Gx*dt + get_last_x_angle()
    gy_angle = Gy*dt + get_last_y_angle()
    gz_angle = Gz*dt + get_last_z_angle()
    return gx_angle, gy_angle, gz_angle

def acc_angle(Ax, Ay, Az):
    radToDeg = 180/3.14159
    ax_angle = math.atan(Ax/math.sqrt(math.pow(Ay,2) + math.pow(Az, 2)))*radToDeg       
    ay_angle = math.atan((-Ay)/math.sqrt(math.pow(Ay,2) + math.pow(Az, 2)))*radToDeg  
    az_angle = math.atan((-Az)/math.sqrt(math.pow(Ax,2) + math.pow(Ax,2)))*radToDeg   
    return ax_angle, ay_angle, az_angle


def set_last_read_angles(x, y, z):
    global last_x_angle, last_y_angle, last_z_angle
    last_x_angle = x
    last_y_angle = y
    last_z_angle = z



DEVICE = "00:04:79:00:0d:ca"

print("eSense address:"),
print(DEVICE)

# Run gatttool interactively.
print("Run gatttool...")
child = pexpect.spawn("gatttool -I")

# Connect to the device.
print("Connecting to "),
print(DEVICE),
child.sendline("connect {0}".format(DEVICE))
child.expect("Connection successful", timeout=5)
print(" Connected!")

child.sendline("char-read-hnd 0x0c")
child.expect("Characteristic value/descriptor: ", timeout=10)
child.expect("\r\n", timeout=10)
print("Start/Stop Value: {0} ".format(child.before.decode("utf-8")))

print("Starting the IMU data sampling....")

child.sendline("char-write-req 0x0c 5335020132")
child.expect("Characteristic value was written successfully", timeout=10)
child.expect("\r\n", timeout=10)
print("Write successful, IMU started publishing")

i = 0

#path = 'Sensor_Data.txt'

#if os.path.exists(path):
#    print("File exists")
#    os.remove(path)

#f = open("Sensor_Data.txt", "w")


while True:
    #try:
    child.sendline("char-read-hnd 0x000e")
    child.expect("Characteristic value/descriptor: ", timeout=10)
    #child.expect("\r\n", timeout=10)
    #print("Raw values: ",child.before.decode("utf-8").split('\r\n'))
    raw = child.before.decode("utf-8").split('\r\n')
    #print(raw)


    try:
        for i in range(1,len(raw)):
            if(len(raw[i]) > 100):
                imu_data = raw[i]
                #print(imu_data)
                #print(len(raw))
                #print(imu_data[76:123])
                imu_values = imu_data[76:123]

                _imu_values = imu_values[12:14]

                #print(imu_values[12:47])
                
                try:
                    gyro_x, gyro_y, gyro_z = getGyroValues(imu_values)
                    accl_x, accl_y, accl_z = getAcclValues(imu_values)

                except:
                    continue
                #print("Gyroscope Reading: {0:.3f} {1:.3f} {2:.3f}".format(gyro_x, gyro_y, gyro_z))
                #print("Accelerometer Reading: {0:.3f} {1:.3f} {2:.3f}".format(accl_x, accl_y, accl_z))
                print("\n")
                dt =  1/50

                # Calculate angle of inclination or tilt for the x and y axes with acquired acceleration vectors
                acc_angle_x, acc_angle_y, acc_angle_z = acc_angle(accl_x, accl_y, accl_z)
                gyr_angle_x, gyr_angle_y, gyr_angle_z = gyr_angle(gyro_x, gyro_y, gyro_z, dt)
                #print(acc_angles)
                #print(gyr_angles)
		

                # filtered tilt angle
                roll, pitch, yaw = c_filtered_angle(acc_angle_x, acc_angle_y, acc_angle_z,  gyr_angle_x, gyr_angle_y, gyr_angle_z)
                print("Roll: {0:.3f}  Pitch: {1:.3f} Yaw: {2:.3f}".format(roll, pitch, yaw))
                set_last_read_angles(gyr_angle_x, gyr_angle_y, gyr_angle_z)
                #f.write("{0:.3f}, {1:.3f}, {2:.3f} \n".format(roll, pitch, yaw))
                 
    
    except pexpect.exceptions.TIMEOUT:
        pass
    
    
#f.close()
