#just used to calibrate the rovers, see notability doc

#!/usr/bin/env python

import time
import serial
import os

#set up serial interface
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)


#calculate check sum, input in decimal
def checkSum(address,command,data):
    tempSum = address + command + data
    afterMask = tempSum & 0b01111111 #add mask
    return afterMask #return checksum number

#used for sending simplified serial
def sendSimplifiedSerial(data):
    hex_bytes = bytes([data])
    ser.write(hex_bytes)

#used for sending data pakets of 8N1 0 to 5v TTL levels
def sendData(address,command,data):
    checkSumValue = checkSum(address,command,data)
    checkSumValue_hex_bytes = bytes([checkSumValue])

    address_hex_bytes = bytes([address])
    command_hex_bytes = bytes([command])
    data_hex_bytes = bytes([data])

    ser.write(address_hex_bytes) #send address
    ser.write(command_hex_bytes) #send command
    ser.write(data_hex_bytes) # send data
    ser.write(checkSumValue_hex_bytes) # send check sum
    print(address_hex_bytes,command_hex_bytes,data_hex_bytes,checkSumValue_hex_bytes)

print("Running...wait 1 mins to start")

#init block for timing
time.sleep(10)
sendData(130,0,30)
sendData(130,4,30)
time.sleep(2)
sendData(130,1,30)
sendData(130,5,30)
time.sleep(2)
sendData(130,0,0) 
sendData(130,4,0) 
time.sleep(10)
#init block for timing

#forward 20FT calibration
sendData(130,0,40)
sendData(130,4,39)
time.sleep(7)
sendData(130,0,41)
sendData(130,4,39)
time.sleep(20.9)

#stop
sendData(130,0,0)
sendData(130,4,0)


print("DONE")

ser.close()

time.sleep(60) #**NEVER** REMOVE
#os.system("sudo shutdown -h now")
