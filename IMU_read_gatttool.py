import pexpect
import time



def hexStrToInt(hexstr):
    val = int(hexstr[0:2],16) + (int(hexstr[3:5],16)<<8)
    if ((val&0x8000)==0x8000): # treat signed 16bits
        val = -((val^0xffff)+1)
    return val



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


while True:

    child.sendline("char-read-hnd 0x0e")
    child.expect("Characteristic value/descriptor: ", timeout=10)
    child.expect("\r\n", timeout=10)
    print("IMU Data: {0} ".format(child.before.decode("utf-8")))


