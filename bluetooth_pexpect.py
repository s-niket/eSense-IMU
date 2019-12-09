import time
import pexpect
import os

os.system('sudo killall bluealsa')
os.system('pulseaudio --start')
address = '00:04:79:00:0D:CA'
def connect_to_esense(address):
    child = pexpect.spawn('sudo bluetoothctl')
    child.sendline('agent on')
    child.sendline('default-agent')
    child.sendline('pair ' + address)
    child.sendline('trust ' + address)
    child.sendline('exit')
    child.close()


connect_to_esense(address)


os.system('pacmd set-default-sink bluez_sink.00_04_79_00_0D_CA.a2dp_sink')
os.system('paplay /home/pi/Desktop/swvader01.wav')
os.system('paplay -d bluez_sink.00_04_79_00_0D_CA /home/pi/Desktop/swvader01.wav')
