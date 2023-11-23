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
SABER_COLOR = 3
CLASH_COLOR = 6
NUM_PIXELS = 124

def init_power_output(status: bool) -> DigitalInOut:
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

def init_audio():
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
    red_led = pwmio.PWMOut(board.D10)
    green_led = pwmio.PWMOut(board.D11)
    blue_led = pwmio.PWMOut(board.D12)
    return red_led, green_led, blue_led

def set_rgb_led(color):
    """Convert from 0-255 (neopixel range) to 65535-0 (pwm range)"""
    red_led.duty_cycle = int(simpleio.map_range(color[0], 0, 255, 65535, 0))
    green_led.duty_cycle = int(simpleio.map_range(color[1], 0, 255, 65535, 0))
    blue_led.duty_cycle = int(simpleio.map_range(color[2], 0, 255, 65535, 0))

# Code initialization
if __name__ == "__main__":
    # Local variables initialization
    MODE = 0
    # Hardware initialization
    wav_list = load_wavs("./sounds")
    switch = init_button()
    external_power = init_power_output(True)
    pixels = init_neopixel()
    audio = init_audio()
    lis3dh = init_accelerometer()
    red_led, green_led, blue_led = init_button_leds()
    set_rgb_led(COLORS[SABER_COLOR])
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
        if MODE == 0:
            print(MODE)
            play_wav(wav_list[0], audio, loop=False)
            for i in range(NUM_PIXELS):
                pixels[i] = COLORS[SABER_COLOR]
                pixels.show()
            play_wav(wav_list[1], audio, loop=True)
            MODE = 1
        # default
        elif MODE == 1:
            x, y, z = lis3dh.acceleration
            accel_total = x * x + z * z
            if lis3dh.tapped:
                MODE = 10
            elif accel_total >= SWING_THRESHOLD:
                MODE = 11
            if switch.short_count == 1:
                MODE = 3
            if switch.long_press:
                audio.stop()
                play_wav(wav_list[19], audio, loop=True)
                MODE = 5
        # clash or move
        elif MODE == 10:
            audio.stop()
            play_wav(wav_list[random.randint(3, 10)], audio, loop=False)
            while audio.playing:
                pixels.fill(WHITE)
                pixels.show()
            pixels.fill(COLORS[SABER_COLOR])
            pixels.show()
            play_wav(wav_list[1], audio, loop=True)
            MODE = 1
        elif MODE == 11:
            audio.stop()
            play_wav(wav_list[random.randint(11, 18)], audio, loop=False)
            while audio.playing:
                pixels.fill(COLORS[SABER_COLOR])
                pixels.show()
            pixels.fill(COLORS[SABER_COLOR])
            pixels.show()
            play_wav(wav_list[1], audio, loop=True)
            MODE = 1
        # turn off
        elif MODE == 3:
            audio.stop()
            play_wav(wav_list[2], audio, loop=False)
            for i in range(99, 0, -1):
                pixels[i] = (0, 0, 0)
                pixels.show()
            time.sleep(1)
            external_power.value = False
            MODE = 4
        # go to startup from off
        elif MODE == 4:
            if switch.short_count == 1:
                external_power.value = True
                MODE = 0
        # change color
        elif MODE == 5:
            if switch.short_count == 1:
                SABER_COLOR = (SABER_COLOR + 1) % 6
                pixels.fill(COLORS[SABER_COLOR])
                pixels.show()
                set_rgb_led(COLORS[SABER_COLOR])
            if switch.long_press:
                play_wav(wav_list[1], audio, loop=True)
                pixels.fill(COLORS[SABER_COLOR])
                pixels.show()
                set_rgb_led(COLORS[SABER_COLOR])
                MODE = 1
