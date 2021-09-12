import TCA9548A
import VL53L1X

TCA9548A.I2C_setup(0x70,0)
tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.set_timing(66000, 70)
tof.start_ranging(3)  # Start ranging
d1 = tof.get_distance()

TCA9548A.I2C_setup(0x70,1)
tof2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof2.open()
tof2.set_timing(66000, 70)
tof2.start_ranging(3)  # Start ranging
d2 = tof2.get_distance()

TCA9548A.I2C_setup(0x70,2)
tof3 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof3.open()
tof3.set_timing(66000, 70)
tof3.start_ranging(3)  # Start ranging
d3 = tof3.get_distance()

print("front:", d1, ",left: ",d2, ",right: ",d3)