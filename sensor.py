import RPi.GPIO as GPIO
from time import sleep

# initialize
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)
valid_read = True

while True:
	print GPIO.input(3)


GPIO.cleanup()
