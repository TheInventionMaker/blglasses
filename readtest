#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name
import serial,time,sys,os
if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/ttyS0", 115200, timeout=1) as arduino:
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            try:
                while True:
                    if  arduino.inWaiting()>0: 
                        answer=arduino.readline().decode('utf-8').rstrip()
                        if answer == 'begin':
                                print("Beginning Image recognition")
                                arduino.write(b"chair, ")
                                arduino.write(b"desk, ")
                                arduino.write(b"charging station\n")
                        elif answer == 'stop':
                                print("Stopping Image recognition")
                        elif answer.find(': ') != -1:
                                print("Username: " + answer.split(': ')[1] + " Password: " + answer.split(': ')[3])
                        elif answer == 'charging':
                                print("Charging. Will check for updates soon")
#                               os.system("pkill -f readtest.py")
                        arduino.flushInput() #remove data after reading
            except KeyboardInterrupt:
                print("Exiting Program")
