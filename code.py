import time
import adafruit_dotstar
import board, analogio, digitalio
import random

# Init LDO2 Pin
ldo2 = digitalio.DigitalInOut(board.LDO2)
ldo2.direction = digitalio.Direction.OUTPUT

THRESHOLD = 25_000
GRADIENT_RATIO = 255 / 50_000


def enable_LDO2(state):
    """Set the power for the second on-board LDO to allow no current draw when not needed."""
    ldo2.value = state
    # A small delay to let the IO change state
    time.sleep(0.035)


def dotstar_color_wheel(wheel_pos):
    """Color wheel to allow for cycling through the rainbow of RGB colors."""
    wheel_pos = wheel_pos % 255

    if wheel_pos < 85:
        return 255 - wheel_pos * 3, 0, wheel_pos * 3
    elif wheel_pos < 170:
        wheel_pos -= 85
        return 0, wheel_pos * 3, 255 - wheel_pos * 3
    else:
        wheel_pos -= 170
        return wheel_pos * 3, 255 - wheel_pos * 3, 0


# Make sure the 2nd LDO is turned on
enable_LDO2(True)

# Create a DotStar instance
dotstar = adafruit_dotstar.DotStar(
    board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True
)

# Create a reference to the ambient light sensor so we can read it's value
light = analogio.AnalogIn(board.AMB)

# Change this to true after reading the code below ;)
isSetup = True

if isSetup == False:
    raise Exception("Board is connected, setup has not been done")

# Create a colour wheel index int
color_index = 0

# TODO: Uncomment for Part 2
led_1 = digitalio.DigitalInOut(board.A0)
led_2 = digitalio.DigitalInOut(board.A1)

led_1.direction = digitalio.Direction.OUTPUT
led_2.direction = digitalio.Direction.OUTPUT

led_1.value = True
led_2.value = True


# Rainbow colours on the Dotstar
while True:
    # Get the R,G,B values of the next colour
    r, g, b = dotstar_color_wheel(color_index)
    # Set the colour on the dotstar
    dotstar[0] = (r, g, b, 0.6)

    # Increase the wheel index. 0 -> 255.
    color_index = light.value * GRADIENT_RATIO

    # TODO: Modify the value of the color index so that it is linearly correlated with the values received from the ambient sensor.

    # TODO: Part 2: Extend the code to use the ambient light sensor values to change which LED gets turned on.

    # is_threshold_reached = light.value > THRESHOLD
    is_threshold_reached = light.value > THRESHOLD
    led_1.value = is_threshold_reached
    led_2.value = not is_threshold_reached

    # Prints out value from Ambient Sensor
    print("Ambient Light Reading: {}".format(light.value))
    print(f"LED 1: {led_1.value}")
    print(f"LED 2: {led_2.value}")

    # Prints out color index
    print("Color Index: {}".format(color_index))

    # Sleep for 15ms so the colour cycle isn't too fast
    time.sleep(0.015)
