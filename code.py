# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import os
import random
import board
import pwmio
import audiocore
import audiobusio
from adafruit_debouncer import Button
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import adafruit_lis3dh
import simpleio
import math

# CUSTOMIZE SENSITIVITY HERE: smaller numbers = more sensitive to motion
HIT_THRESHOLD = 120
SWING_THRESHOLD = 130
RED = (255, 0, 0)
YELLOW = (125, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 125, 255)
BLUE = (0, 0, 255)
PURPLE = (125, 0, 255)
WHITE = (255, 255, 255)
COLORS = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE]
CLASH_COLOR = 6
NUM_PIXELS = 124

def init_power_output() -> DigitalInOut:
    """Command the 5V power output (turned off to save battery)"""
    ext_power = DigitalInOut(board.EXTERNAL_POWER)
    ext_power.direction = Direction.OUTPUT
    ext_power.value = True
    return ext_power

def load_wavs(wav_path: str) -> list[str]:
    """Read the list of WAV files in memory and return it"""
    wavs = []
    for filename in os.listdir(wav_path):
        if filename.lower().endswith('.wav') and not filename.startswith('.'):
            wavs.append(f"{wav_path}/{filename}")
    wavs.sort()
    return wavs

def init_audio() -> audiobusio.I2SOut:
    """Initialize audio module"""
    return audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)

def play_wav(filename, audio_device, loop=False) -> None:
    """
    Play a WAV file in the 'sounds' directory.
    :param name: partial file name string, complete name will be built around
                 this, e.g. passing 'foo' will play file 'sounds/foo.wav'.
    :param loop: if True, sound will repeat indefinitely (until interrupted
                 by another sound).
    """
    try:
        wave_file = open(filename, "rb")
        wave = audiocore.WaveFile(wave_file)
        audio_device.play(wave, loop=loop)
    except:  # pylint: disable=bare-except
        return

def init_button() -> Button:
    """Initialize the external button"""
    pin = DigitalInOut(board.EXTERNAL_BUTTON)
    pin.direction = Direction.INPUT
    pin.pull = Pull.UP
    return Button(pin, long_duration_ms = 1000)

def init_neopixel(num_pixels: int = NUM_PIXELS, brightness: float = 0.8) -> neopixel.NeoPixel:
    """Initialize NeoPixel LED strip"""
    tmp_pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels, auto_write=True)
    tmp_pixels.brightness = brightness
    return tmp_pixels

def init_accelerometer() -> adafruit_lis3dh.LIS3DH_I2C:
    """Initialize onboard LIS3DH"""
    tmp_i2c = board.I2C()
    tmp_int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
    tmp_lis3dh = adafruit_lis3dh.LIS3DH_I2C(tmp_i2c, int1=tmp_int1)
    # Accelerometer Range (can be 2_G, 4_G, 8_G, 16_G)
    tmp_lis3dh.range = adafruit_lis3dh.RANGE_2_G
    
    tmp_lis3dh.set_tap(1, HIT_THRESHOLD)
    return tmp_lis3dh

def init_button_leds() -> list[pwmio.PWMOut]:
    """Initialize RGB led in the main button"""
    tmp_red_led = pwmio.PWMOut(board.D10)
    tmp_green_led = pwmio.PWMOut(board.D11)
    tmp_blue_led = pwmio.PWMOut(board.D12)
    return tmp_red_led, tmp_green_led, tmp_blue_led

def set_rgb_led(color, in_red_led, in_green_led, in_blue_led):
    """Convert from 0-255 (neopixel range) to 65535-0 (pwm range)"""
    in_red_led.duty_cycle = int(simpleio.map_range(color[0], 0, 255, 65535, 0))
    in_green_led.duty_cycle = int(simpleio.map_range(color[1], 0, 255, 65535, 0))
    in_blue_led.duty_cycle = int(simpleio.map_range(color[2], 0, 255, 65535, 0))

def read_gesture(lis3dh, last_x, last_y, last_z):
    """Read gestures from the sword"""
    x, y, z = lis3dh.acceleration
    x = abs(x / 9.81)
    y = abs(y / 9.81)
    z = abs(z / 9.81)
    if last_x > 0 and last_y > 0 and last_z > 0:
        dx = abs(last_x - x)
        dy = abs(last_y - y)
        dz = abs(last_z - z)
        accel_total = dx*dy*1000
        #print(accel_total)
        if lis3dh.tapped:
            return 10, 0, 0, 0
        elif accel_total >= 1:
            return 11, 0, 0, 0
    return 1, x, y, z

def main(saber_color: int = 0):
    """Main program code"""
    # Local variables initialization
    mode = 4
    # Hardware initialization
    wav_list = load_wavs("./sounds")
    switch = init_button()
    external_power = init_power_output()
    pixels = init_neopixel()
    audio = init_audio()
    lis3dh = init_accelerometer()
    red_led, green_led, blue_led = init_button_leds()
    set_rgb_led(COLORS[saber_color], red_led, green_led, blue_led)
    # Temporary variables
    last_x = 0.0
    last_y = 0.0
    last_z = 0.0
    idling = 0
    # Main state machine
    # 0: startup
    # 1: read status
    # 2:
    # 3: turning off
    # 4: soft restart
    # 5: change color
    # 10: hit
    # 11: swing
    while True:
        switch.update()
        # startup
        if mode == 0:
            set_rgb_led(COLORS[saber_color], red_led, green_led, blue_led)
            play_wav(wav_list[0], audio, loop=False)
            for i in range(NUM_PIXELS):
                pixels[i] = COLORS[saber_color]
            play_wav(wav_list[1], audio, loop=True)
            mode = 1
        # default
        elif mode == 1:
            if switch.short_count == 1:
                mode = 3
            elif switch.long_press:
                audio.stop()
                play_wav(wav_list[19], audio, loop=True)
                mode = 5
            else:
                mode, last_x, last_y, last_z = read_gesture(lis3dh, last_x, last_y, last_z)
            # if lis3dh.tapped:
            #      MODE = 10
            # elif accel_total >= SWING_THRESHOLD:
            #     MODE = 11
        # clash or move
        elif mode == 10:
            audio.stop()
            play_wav(wav_list[random.randint(3, 10)], audio, loop=False)
            while audio.playing:
                pixels.fill(WHITE)
            pixels.fill(COLORS[saber_color])
            play_wav(wav_list[1], audio, loop=True)
            mode = 1
        elif mode == 11:
            audio.stop()
            play_wav(wav_list[random.randint(11, 18)], audio, loop=False)
            while audio.playing:
                pixels.fill(COLORS[saber_color])
            pixels.fill(COLORS[saber_color])
            play_wav(wav_list[1], audio, loop=True)
            mode = 1
        # turn off
        elif mode == 3:
            audio.stop()
            play_wav(wav_list[2], audio, loop=False)
            for i in range(NUM_PIXELS):
                pixels[NUM_PIXELS - 1 - i] = (0, 0, 0)
            external_power.value = False
            mode = 4
        # go to startup from off
        elif mode == 4:
            if switch.short_count >= 1:
                external_power.value = True
                mode = 0
            else:
                if idling > 3000:
                    idling = 0
                elif idling > 2900:
                    set_rgb_led(COLORS[saber_color], red_led, green_led, blue_led)
                else:
                    set_rgb_led((0,0,0), red_led, green_led, blue_led)
                idling += 1
                external_power.value = False
        # change color
        elif mode == 5:
            if switch.short_count >= 1:
                saber_color = (saber_color + 1) % 6
                pixels.fill(COLORS[saber_color])
                set_rgb_led(COLORS[saber_color], red_led, green_led, blue_led)
            if switch.long_press:
                play_wav(wav_list[1], audio, loop=True)
                pixels.fill(COLORS[saber_color])
                set_rgb_led(COLORS[saber_color], red_led, green_led, blue_led)
                mode = 1


# Code initialization
if __name__ == "__main__":
    main()
