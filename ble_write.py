import gatt
import sys

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
        

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))


        imu_service = next(
            s for s in self.services
            if s.uuid == '0000ff06-0000-1000-8000-00805f9b34fb')
       

        for c in imu_service.characteristics:
            print("UUIDs :{0}".format(c.uuid))


        firmware_version_characteristic = next(
            c for c in imu_service.characteristics
            if c.uuid == '00000009-0000-1000-8000-00805f9b34fb')

        firmware_version_characteristic.read_value()

    def characteristic_value_updated(self, characteristic, value):
        print("Firmware version:", value.decode("utf-8"))



mac_addr = '00:04:79:00:0d:ca'
# mac_addr = '00:04:79:00:0F:54'
device = AnyDevice(mac_address=mac_addr, manager=manager)
device.connect()

manager.run()
