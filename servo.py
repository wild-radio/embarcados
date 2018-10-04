import RPi.GPIO as GPIO
from time import sleep

# initialize
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(0o3, GPIO.OUT)
GPIO.setup(0o5, GPIO.OUT)

# setup frequency
pwm1=GPIO.PWM(0o3, 50)
pwm2=GPIO.PWM(0o5, 50)

# starts with 0% duty cicle
pwm1.start(0)
pwm2.start(0)

# changes servo 1 angle
def SetAngle1(angle):
    duty = angle / 18 + 2
    GPIO.output(0o3, True)
    pwm1.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(0o3, False)
    pwm1.ChangeDutyCycle(0)

# changes servo 2 angle 
#TOMAR CUIDADO, ESSA PORRA PODE QUEBRAR O SUPORTE
def SetAngle2(angle):
    duty = angle / 18 + 2
    GPIO.output(0o5, True)
    pwm2.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(0o5, False)
    pwm2.ChangeDutyCycle(0)



while True:
    ang1 = int(input("Angulo 1 de 0 a 180º         "))
    SetAngle1(ang1)
    ang2 = int(input("Angulo 2 de 0 a 180º         "))
    SetAngle2(ang2)
    quit = int(input("digite 1 para sair ou outra coisa para mudar de novo os angulos          "))
    if quit == 1:
        break
    

pwm1.stop()
pwm2.stop()
GPIO.cleanup()
