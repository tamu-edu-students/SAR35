#!/usr/bin/env python

import time
import serial

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


time.sleep(2)
sendData(130,0,64) #test given example
time.sleep(2)

ser.close()


