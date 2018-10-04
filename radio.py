import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(0o7, GPIO.OUT)
GPIO.output(0o7, False)


while True:
    i = int(input("Digite um numero:"))
    if i == 1:
        GPIO.output(0o7, True)
    if i == 2:
        GPIO.output(0o7, False)
        
