import argparse
import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import numpy as np

parser = argparse.ArgumentParser(description="Motor testing script!")
parser.add_argument('-e', '--esc', type=int, default=1, help='ESC channel (default: 1)')
parser.add_argument('-s', '--servo', type=int, default=0, help='Servo channel (default: 0)')
parser.add_argument('-i', '--initialize', type=int, default="0", help='Is the motor running for the first time since being switched on? (default: 0)')
parser.add_argument('--extra_option', type=str, default="", help='Message to explain the option (default: empty string)')  # Template for additional arguments

args = parser.parse_args()

ESC_CHANNEL = args.esc
SERVO_CHANNEL = args.servo

# If the motor is running for the first time since being switched on, the ESC needs to be "armed"
# (meaning that we need to send a neutral signal for 2 seconds)
arm_ESC = args.initialize

extra_argument = args.extra_option


# === Constants ===
FREQ = 60    # Standard ESC expects 50–60Hz
NEUTRAL = 1500
FORWARD = 1600
BACKWARD = 1400
MAX = 1900
MIN = 1200

# Setup I2C bus and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = FREQ

def set_pwm(channel, microseconds):
    """
    Translates microseconds (e.g., 1500) into the 0-0xFFFF (0-65535) scale
    required by the slide's instruction:
    pca.channels[CHANNEL].duty_cycle = <scaled signal>
    """
    period_in_microseconds = 1000000 / 60
    duty_cycle = int((microseconds / period_in_microseconds) * 65535)
    
    # Safety check to keep it within 16-bit limits
    if duty_cycle > 65535: duty_cycle = 65535
    
    pca.channels[channel].duty_cycle = duty_cycle

try:
    # "Send a PWM pulse that's high for 1.5 ms... have this last for 2 seconds"
    print(">>> Arming ESC (1.5ms for 2 seconds)...")
    set_pwm(ESC_CHANNEL, NEUTRAL)
    time.sleep(2)

    print(">>> MOVING FORWARD!")
    set_pwm(ESC_CHANNEL, FORWARD) 
    time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping early...")

finally:
    print(">>> Tearing down (Resetting to Neutral and De-initializing)")
    set_pwm(ESC_CHANNEL, NEUTRAL) # Safety stop first
    time.sleep(0.1)
    pca.deinit() # The specific command from your slide
    print(">>> Done.")