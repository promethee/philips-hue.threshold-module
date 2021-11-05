# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import math
import os
import digitalio
import board
import time
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium
import busio
import adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

# Configuration for CS and DC pins for Raspberry Pi
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000  # The pi can be very fast!
# Create the ST7789 display:
display = st7789.ST7789(
    board.SPI(),
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

FLIP = os.environ.get('FLIP', False)
WIDTH = display.height
HEIGHT = display.width
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),
    (255, 128, 0),
    (255, 255, 0),
    (128, 255, 0),
    (0, 255, 0),
    (0, 255, 128),
    (0, 255, 255),
    (0, 128, 255),
    (0, 0, 255),
    (255, 0, 255),
    (255, 0, 128),
]
COLORS_LENGTH = len(COLORS)
index = 0

font_ui = ImageFont.truetype(RobotoMedium, 64)
font = ImageFont.truetype(RobotoMedium, 32)
font_small = ImageFont.truetype(RobotoMedium, 32)
font_smiley = ImageFont.truetype('./CODE2000.TTF', 32)
img = Image.new("RGB", (WIDTH, HEIGHT), 0)
draw = ImageDraw.Draw(img)

index = 0
paused = False
threshold = -1
distances = []
DISTANCES_MAX_LEN = (WIDTH/4) if (WIDTH % 2 == 0) else ((WIDTH - 1)/4)

def format(distance):
    if (distance > 1000):
        return str(distance)[0:1] + ' m' + str(distance)[1:3]
    if (distance > 100 and distance < 999):
        return str(distance)[0:2] + 'cm' + str(distance)[2:3]
    if (distance > 0 and distance < 99):
        return str(distance)[0:2] + 'mm'

def get_ratio(distance, threshold):
    return round((distance / threshold) * 100) / 100

def show_range(distance, ratio):
    percent = str(round(ratio * 100)) + '%'
    text = format(distance)
    pw, ph = draw.textsize(percent, font=font_small)
    draw.text((WIDTH - pw, HEIGHT - 64), percent, font=font_small, fill=WHITE)
    draw.text((int(WIDTH * 0.6), HEIGHT - 32), text, font=font_small, fill=WHITE)

def show_credits():
    global index
    emoji = "¯\_(ツ)_/¯"
    lw, lh = draw.textsize(emoji, font=font_smiley)
    draw.text(((WIDTH/2) - (lw/2), int(HEIGHT*0.15)), emoji, font=font_smiley, fill=COLORS[index])
    draw.text((0, int(HEIGHT*0.4)), "promethee", font=font, fill=COLORS[index])
    draw.text((0, int(HEIGHT*0.7)), "@github", font=font, fill=COLORS[index])

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

while True:
    distance = vl53.range

    if (distance > threshold):
        threshold = distance

    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)
    if not buttonB.value:
        FLIP = not FLIP
        time.sleep(0.3)
    if not buttonA.value:
        paused = not paused
        time.sleep(0.3)
    if not paused:
        index = index + 1 if index < len(COLORS) - 1 else 0

    ratio = get_ratio(distance, threshold)

    show_range(distance, ratio)
    show_credits()
    ROTATION = 270 if FLIP else 90
    display.image(img, ROTATION)
