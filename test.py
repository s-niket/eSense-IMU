
import sys
import time


import bluetooth

# sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM)


print("Performing inquiry...")

nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True,
                                            flush_cache=True, lookup_class=False)

print("Found {} devices".format(len(nearby_devices)))

addr = None

for addr1, name in nearby_devices:
    try:
        print("   {} - {}".format(addr1, name))
        if name=="eSense-0924":
            addr = addr1
    except UnicodeEncodeError:
        print("   {} - {}".format(addr1, name.encode("utf-8", "replace")))
try:
    print("eSense Addr {0}".format(addr)) 

except: 
    print("Couldnt find eSense, bye......")
    sys.exit(0)


if addr is not None:
    
    services = bluetooth.find_service(address=addr) # ,uuid="ff06")
    print(services)
'''
    # search for the eSense service
    uuid = "0000ff06-0000-1000-8000-00805f9b34fb"
    # uuid = None
    for i in range(0,2):
        print("Try {0}".format(i))
        service_matches = bluetooth.find_service(uuid=uuid) #, address=addr)
        time.sleep(2)

    if len(service_matches) == 0:
        print("Couldn't find the eSense service.")
        sys.exit(0)

    print(service_matches)
'''

'''
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print("Connecting to \"{}\" on {}".format(name, host))

    # Create the client socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    print("Connected. Type something...")
    while True:
        data = input()
        if not data:
            break
        sock.send(data)

    sock.close()
    '''
