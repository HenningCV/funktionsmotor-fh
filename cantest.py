#!/usr/bin/python
# coding=utf-8

import subprocess
import time

process = subprocess.Popen(["sudo","ip","link","set","can0","type","can","bitrate","500000"])
process.wait()
print("1")
process = subprocess.Popen(["sudo","ifconfig","can0","txqueuelen","1000"])
process.wait()
print("2")
process = subprocess.Popen(["sudo","ifconfig","can0","up"])
process.wait()
time.sleep(1)

can_id_manifold = 200
ads_manifold_voltage = 0.002
voltage_treshold = 0.003

'''
while True:
    print("loop")
    print("...")
    process = subprocess.Popen(["cansend","can0","128#DEADBEEFDEADBEEF"])
    process.wait()
    #time.sleep(0.01)
'''
def sensor_ts200(x):
    return 22.2*x**2 + 432.6*x - 387.88

def prepareCanDataString(can_id, raw_value, function_value, multiplier):
    value_hex = hex(int(abs(function_value*multiplier))).split('x')[-1].zfill(4)
    voltage_hex = hex(int(abs(raw_value*1000))).split('x')[-1].zfill(4)
    can_output = str(can_id) + "#" + value_hex + voltage_hex
    print(can_output)
    return can_output

def cleanse_value(value):
    v = "str"
    if value <= voltage_treshold:
        v = 0.0
        print("Value under threshold.")
    else:
        v = value
        print("Value above threshold.")
    return v


process = subprocess.Popen(["cansend","can0",prepareCanDataString(can_id_manifold, cleanse_value(ads_manifold_voltage), sensor_ts200(cleanse_value(ads_manifold_voltage)), 1)])
