# Add your Python code here. E.g.
from microbit import *
import music
import time
import random


# tunes for the "guess the tone" game

gameOver = False

tunes = [
    ["C4:4", 'C', 'D', 'D', 'E', 'E', 'x', 'G', 'G', 'E', 'E', 'A', 'A', 'x'],
    ["C4:4", "D", "E", "C", "C", "D", "E", 'x', "C",
        "E", "F", "G:8", "E:4", "F", 'x', "G:8"],
    ["C2:2"] + [letter for letter in "ABCDExFGFEDCBABxCDEFxGFEDCxBA"]
]


class Servo:

    def __init__(self, pin, freq=50, min_us=600, max_us=2400, angle=180):
        self.min_us = min_us
        self.max_us = max_us
        self.us = 0
        self.freq = freq
        self.angle = angle
        self.analog_period = 0
        self.pin = pin
        analog_period = round((1/self.freq) * 1000)  # hertz to miliseconds
        self.pin.set_analog_period(analog_period)

    def write_us(self, us):
        us = min(self.max_us, max(self.min_us, us))
        duty = round(us * 1024 * self.freq // 1000000)
        self.pin.write_analog(duty)
        self.pin.write_digital(0)  # turn the pin off

    def write_angle(self, degrees=None):
        degrees = degrees % 360
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.angle
        self.write_us(us)


def game1Guess(level, pos):

    display.clear()

    timer = 5

    while(timer):

        timer = timer - 1

        music.play(['A1:1'])

        sleep(1000 // (level+1))  # each level, we get faster:
        # 1000 / 1 = 1000,
        # 1000 / 2 = 500,
        # 1000 / 3 = 333, etc.

        if pos % 2:  # what position was the x?
            if button_a.was_pressed():  # a was pressed correctly.
                return True
            elif button_b.was_pressed():  # b was pressed incorrectly.
                return False
        else:
            if button_b.was_pressed():  # b was pressed correctly
                return True
            elif button_a.was_pressed():  # a was pressed incorrectly.
                return False

    # nothing was pressed, which is incorrect;
    return False


def game1():
    # Guess the tone
    lives = 3

    for level, tune in enumerate(tunes):
        for pos, tone in enumerate(tune):

            if pos % 2 == 0:
                display.show(Image.ARROW_W)
            else:
                display.show(Image.ARROW_E)

            if tone != 'x':
                music.play([tone])
            else:
                correctGuess = game1Guess(level, pos)

                if correctGuess:
                    music.play(music.POWER_UP)
                    display.show(Image.HAPPY)
                else:
                    lives -= 1
                    music.play(music.POWER_DOWN)
                    display.show(Image.SAD)

                sleep(1000)

            if lives == 0:
                gameOver = True
                return

    # success! onwards to game 2
    game2()


def game2():
    # race to the point
    # read the analogue pin and get faster by the time we get to the point

    lives = 3

    for level in range(5):

        point = random.randint(0, 1023)

        reading = 0
        timing = time.ticks_ms()

        while reading != point:
            reading = pin1.read_analog()

            difference = abs(point - reading)

            # play tone indicating; faster tone => closer
            music.pitch(440, difference)
            # if time is too large; then we lose a life.

            if time.ticks_diff(time.ticks_ms(), timing) > ((5-level) * 1000):
                lives -= 1
                music.play(music.POWER_DOWN)
                display.show(Image.SAD)
                sleep(1000)
                break

        if lives == 0:
            gameOver = True
            return

    game3()


def game3():
    # balance the ship.

    # This is to learn how to spin the servo in a balancing game.

    ship = Servo(pin2)  # what pin is the servo on?

    timer = time.ticks_ms()

    while True:

        point = random.randint(0, 1023)
        value = accelerometer.get_x()

        difference = point - value

        if difference > 20:
            display.show("R")
        elif difference < -20:
            display.show("L")
        else:
            display.show("-")

        ship.write_angle(90 + (difference/1023)*90)

        if difference < 20:
            if time.ticks_ms() - timer > 3000:
                #must hold it for more than 3 seconds
                return

        else:
            timer = time.ticks_ms()



while True:

    # Start up
    music.play(music.POWER_UP)
    display.show(Image.HEART)
    sleep(2000)

    # start playing game one
    game1()

    # Now the games are over; did we reach game over?

    if gameOver:
        #play sad things
        display.show(Image.SAD)
        music.play(music.WAWAWAWAA)

    else:  # we didn't so it must have been completed!
        display.show(Image.HAPPY)
        music.play(music.NYAN)

    sleep(5000)  # 5 seconds.