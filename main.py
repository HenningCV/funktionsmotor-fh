#!/usr/bin/python3
# coding=utf-8
 
import time
import os
import threading
import RPi.GPIO as GPIO
from subprocess import Popen, run, PIPE
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_extended_bus import ExtendedI2C as i2cx
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import pigpio

##################
DEBUG = False
TESTMODE = False
##################

can_bitrate = "500000"
analog_digital_1 = 72  # 0x48 - Standard address, without jumper
analog_digital_2 = 75  # 0x4b - with jumper between ADDR and SCl
voltage_treshold = 0.003
fuel_freq_cycles = 50

# Create the I2C bus
maini2c = i2cx(1)
displayi2c = i2c(port=4, address=0x3C)

# Create objects
ads1 = ADS.ADS1115(maini2c, address=analog_digital_1)
ads2 = ADS.ADS1115(maini2c, address=analog_digital_2) 
device = ssd1306(displayi2c)
freq_gpio = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(freq_gpio, GPIO.IN)
if (TESTMODE == True):
    pi1 = pigpio.pi()

# CAN IDs
can_id_manifold = 200  # Kruemmer
can_id_cat      = 201  # Katalysator
can_id_oilsump  = 202  # Oelwanne
can_id_rpm      = 203  # Drehzahl
can_id_power    = 204  # Leistung
can_id_torque   = 205  # Moment
can_id_fuel     = 206  # Kraftstoffverbrauch

# ADS
ads_manifold = AnalogIn(ads1, ADS.P0)
ads_cat = AnalogIn(ads1, ADS.P1)
ads_oilsump = AnalogIn(ads1, ADS.P2)
ads_rpm = AnalogIn(ads1, ADS.P3)
ads_power = AnalogIn(ads2, ADS.P1)
ads_torque = AnalogIn(ads2, ADS.P2)

# Wertefunktionen
def sensor_ts200(x):
    return 22.2*x**2 + 432.6*x - 387.88

def sensor_pt1000(x):
    return 732.6*x**2 - 115.12*x - 94.506

def sensor_rpm(x):
    return -3.8191*x**2 +2009.8*x + 0.1461

def sensor_torque(x):
    return -0.4462*x**2 + 252.29*x - 0.3436

def sensor_power(x):
    return 6.3675*x**2 + 48.376*x + 0.2449

def aic1204(hz):
    ppl = 2000
    return hz * 3600 / ppl

##################


print("Searching for i2c devices on main i2c bus (1: 2x analog-digital)")
process = Popen(["i2cdetect","-y","1"])
process.wait()
print("")
print("Searching for i2c devices on multiplex i2c bus (4: display)")
process = Popen(["i2cdetect","-y","4"])
process.wait()
print("")
time.sleep(2)

# Setup
print("Setting up CAN device")
process = Popen(["sudo","ip","link","set","can0","type","can","bitrate", can_bitrate])
process.wait()
print("1")
process = Popen(["sudo","ifconfig","can0","txqueuelen","1000"])
process.wait()
print("2")
process = Popen(["sudo","ifconfig","can0","up"])
process.wait()
time.sleep(1)

m_freq = 0  # initialize value

def prepareCanDataString(can_id, raw_value, function_value, multiplier):
    value_hex = hex(int(abs(function_value*multiplier))).split('x')[-1].zfill(4)
    voltage_hex = hex(int(abs(raw_value*1000))).split('x')[-1].zfill(4)
    can_output = str(can_id) + "#" + value_hex + voltage_hex
    return can_output

def display_text(right, top, content):
    oled_font = ImageFont.truetype('FreeSans.ttf', 14)
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline = "white", fill = "black")
        draw.text((right, top), content, font = oled_font, fill = "white")

def cleanse_value(value):
    if value <= voltage_treshold:
        value = 0.0
    else:
        value = value
    return value

def get_freq():
    global m_freq
    NUM_CYCLES = fuel_freq_cycles
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
        GPIO.wait_for_edge(freq_gpio, GPIO.FALLING)
    duration = time.time() - start      # time taken for the loop
    frequency = NUM_CYCLES / duration   # in Hz
    m_freq = round(frequency, 3)
    threading.Timer(1, get_freq).start()

threading.Timer(1, get_freq).start()

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

display_text(15, 5, "Ready")
time.sleep(1)
display_text(15, 5, "Start")
time.sleep(1)

if (TESTMODE == True):
    pi1.set_PWM_frequency(20, 200)
    pi1.set_PWM_dutycycle(20, 128)

while True:
    error_thrown = False
    start = time.time()

    manifold_voltage = cleanse_value(ads_manifold.voltage)
    process = Popen(["cansend","can0",prepareCanDataString(can_id_manifold, manifold_voltage, sensor_ts200(manifold_voltage), 1)])
    cat_voltage = cleanse_value(ads_cat.voltage)
    process = Popen(["cansend","can0",prepareCanDataString(can_id_cat, cat_voltage, sensor_ts200(cat_voltage), 1)])
    oilsump_voltage = cleanse_value(ads_oilsump.voltage)
    process = Popen(["cansend","can0",prepareCanDataString(can_id_oilsump, oilsump_voltage, sensor_pt1000(oilsump_voltage), 1)])
    rpm_voltage = cleanse_value(ads_rpm.voltage)
    process = Popen(["cansend","can0",prepareCanDataString(can_id_rpm, rpm_voltage, sensor_rpm(rpm_voltage), 1)])
    power_voltage = cleanse_value(ads_power.voltage)
    process = Popen(["cansend","can0",prepareCanDataString(can_id_power, power_voltage, sensor_power(power_voltage), 100)])
    torque_voltage = cleanse_value(ads_torque.voltage)
    process = Popen(["cansend","can0",prepareCanDataString(can_id_torque, torque_voltage, sensor_torque(torque_voltage), 100)])
    process = Popen(["cansend","can0",prepareCanDataString(can_id_fuel, m_freq, aic1204(m_freq), 100)])

    end = time.time()
    if (DEBUG == False):
      clearConsole()

    if (error_thrown == False):
      display_text(15, 5, "OK: " + str(int((end - start)*1000)) + " ms")
    print("Manifold: ","{:>5.3f}".format(manifold_voltage) + " V")
    print("Cat:      ","{:>5.3f}".format(cat_voltage) + " V")
    print("Oilsump:  ","{:>5.3f}".format(oilsump_voltage) + " V")
    print("RPM:      ","{:>5.3f}".format(rpm_voltage) + " V")
    print("Power:    ","{:>5.3f}".format(power_voltage) + " V")
    print("Torque:   ","{:>5.3f}".format(torque_voltage) + " V")
    print("Frequency: " + str(m_freq) + " Hz")
    print()
    print("Time in Milliseconds: " + str(int((end - start)*1000)))
    print("---------------------------------------------------")
