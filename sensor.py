import RPi.GPIO as GPIO
from time import sleep

# initialize
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(0o13, GPIO.IN)
valid_read = True

while True:
    if GPIO.input(11):
        valid_read = False
        print "ó o cuzao passando"
    else:
        valid_read = True


GPIO.cleanup()
