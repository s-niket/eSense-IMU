import pexpect
import time
import datetime as dt
import matplotlib.pyplot as plt


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
                gyro_x, gyro_y, gyro_z = getGyroValues(imu_values)
                accl_x, accl_y, accl_z = getAcclValues(imu_values)
                print("Gyroscope Reading: {0:.3f} {1:.3f} {2:.3f}".format(gyro_x, gyro_y, gyro_z))
                print("Accelerometer Reading: {0:.3f} {1:.3f} {2:.3f}".format(accl_x, accl_y, accl_z))
                
            
               # plt.scatter(i, accl_x)
               # plt.pause(0.001)
               # i+=1

                time.sleep(0.001)
                print("\n")
    
        #plt.show() 
    except:
        pass
    
    

    



