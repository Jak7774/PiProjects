#!/usr/bin/python3
from urllib.request import urlopen
import json
import time
import datetime
import random
import board
import neopixel
import RPi.GPIO as GPIO

#--------------------------------------------------
# Setup
#--------------------------------------------------

# --- Parameters for Weather API --- # 

apikey = "" # Key to access API link for data
# Location to check weather - currently Westminster
lati = "51.494720"
longi = "-0.135278"

# --- Parameters for Neopixels --- #

LED_BRIGHTNESS = 0.2 # 0 for darkest and 1 for brightest
pixel_pin = board.D18 # Pin that the lights are connected
num_pixels = 240 # Number of Pixels
ORDER = neopixel.GRB # Define prder to be Green, Red, Blue

# Input parameters into the stairs variable
strip = neopixel.Neopixel(pixel_pin, brightness = LED_BRIGHTNESS, auto_write = False, pixel_order = ORDER)
strip.fill((0, 0, 0)) # Make sure all off
strip.show() # Auto Write is False so this line always needed when changing lights

# --- Parameters for PIR Sensor --- #

GPIO.setmode(GPIO.BCM)
PIR_PIN = 7
GPIO.setup(PIR_PIN, GPIO.IN)

#--------------------------------------------------
# Light Functions
#--------------------------------------------------

# --- Turn on Lights in Temperature Colours --- #

def color(strip, color, start, end): # Credit 
    for i in range(start, end):
        strip[i] = color
    strip.show()

def lights(temp):
    if temp > 0: 
        color(strip, (75, 75, 255), 1, 40) # Light Blue
    if temp > 5:
        color(strip, (0, 255, 0), 41, 80) # Dark Green
    if temp > 10:
        color(strip, (75, 255, 75), 81, 120) # Light Green
    if temp > 15:
        color(strip, (255, 100, 0), 121, 160) # Yellow
    if temp > 20: 
        color(strip, (255, 50, 0), 161, 200) # Orange
    if temp > 25:
        color(strip, (255, 0, 0), 201, 239) # Red
    else:
        return

# --- Rain pattern if Current Conditions = Rain --- #

def rain():
    strip.show()
    for x in range(2000):
        # Random Colors for RGB input
        r = random.randint(0, 1) 
        g = random.randint(0, 1)
        b = random.randint(0, 255)
        # Pick 3 Random Pixels to Change (J, K, L)
        j = random.randrange(0, num_pixels - 1, 3)
        k = random.randrange(1, num_pixels - 1, 3)
        l = random.randrange(2, num_pixels - 1, 3)
        # Turn on Strip
        strip[j] = (r, g, b)
        strip[k] = (r, g, b)
        strip[l] = (r, g, b)
        strip.show()
    return 

# --- Info from API and Call Rain/Temp function --- #

def MOTION(PIR_PIN):
    url = "https://api.forecast.io/forecast/"+apikey+"/"+lati+","+longi+"?units=si"+"&"+"exclude=minutely,hourly,daily,alerts,flags"
    meteo = urlopen(url).read() # Weather from Website
    meteo = meteo.decode('utf-8')
    weather = json.loads(meteo)

    # Current Parameters
    currentTemp = weather['currently']['temperature']
    currentConditions = weather['currently']['icon']

    # Compare Current Temp/Conditions to choose function
    color(strip, (0, 0, 255), 0, 0) # First LED be Blue if Temp is < 0
    if currentConditions == "rain":
        print("Current Weather is ", currentConditions)
        rain()
    else:
        print("Current Temp is ", currentTemp)
        lights(currentTemp)
        time.sleep(30) # Wait 30 Seconds before turning off
    
    strip.fill((0, 0, 0))
    strip.show()
    return

# --- Night Light for walking downstairs at light --- #

first_led = 1
last_led = 239

def NightLight(PIR_PIN):
    print("Night Light Activated!")
    color(strip, (255, 255, 255), 0, 0)
    for i in range(1, 240):
        color(strip, (255, 255, 255), i, i)
        if i > 40:
            color(strip, (0, 0, 0), i-40, i-40)
    
    print("Turning Off")
    for i in range(239, 39, -1):
        color(strip, (255, 255, 255), i-40, i)
        color(strip, (0, 0, 0), i, i)
    for i in range(39, -1, -1):
        color(strip, (0, 0, 0), i, i)
    return

#--------------------------------------------------
# Time Check (Switch Functions based on Time of Day)
#--------------------------------------------------

start_time = 8
end_time = 21

def TimeCheck(PIR_PIN):
    x = datetime.datetime.now()
    now = x.hour
    if start_time <= now <= end_time:
        MOTION(PIR_PIN)
    else:
        NightLight(PIR_PIN)
    return

#--------------------------------------------------
# Start the Script and Callback
#--------------------------------------------------

print("Ready")

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback = TimeCheck)
    while 1:
        time.sleep(10)
    
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
