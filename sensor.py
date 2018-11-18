import RPi.GPIO as GPIO
from time import sleep

# initialize
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN)
try:
	while True:
		print GPIO.input(40)
		sleep(1)

	GPIO.cleanup()


except:
	GPIO.cleanup() #reset all GPIO
	print ("Program ended")
