import RPi.GPIO as GPIO
import numpy as np
import cv2
from time import sleep

# initialize
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(0o3, GPIO.OUT)
GPIO.setup(0o5, GPIO.OUT)
cam = cv2.VideoCapture(0) #starts cam capturing
cv2.namedWindow("test")
img_counter = 0 #picture_name counter

# setup frequency
pwm1=GPIO.PWM(0o3, 50)
pwm2=GPIO.PWM(0o5, 50)

# starts with 0% duty cicle
pwm1.start(0)
pwm2.start(0)
img_counter = 0

# changes servo 1 angle
def SetAngle1(angle):
    duty = angle / 18 + 2
    GPIO.output(0o3, True)
    pwm1.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(0o3, False)
    pwm1.ChangeDutyCycle(0)

# changes servo 2 angle
def SetAngle2(angle):
    duty = angle / 18 + 2
    GPIO.output(0o5, True)
    pwm2.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(0o5, False)
    pwm2.ChangeDutyCycle(0)


while True:
    ret, frame = cam.read()
    cv2.imshow("test", frame)
    if not ret:
        break
    k = cv2.waitKey(1)

    if k%256 == 49:
        # 1 pressed
        print("1")
        ang1 = int(input("Angulo 1 de 0 a 180º     "))
        SetAngle1(ang1)
    elif k%256 == 50:
        # 2 pressed
        print("2")
        ang2 = int(input("Angulo 2 de 0 a 180º     "))
        SetAngle2(ang2)
    elif k%256 == 32:
        # SPACE pressed
        print("3")
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
    elif k%256 == 27:
        print("ESC")
        break
    
    
    

pwm1.stop()
pwm2.stop()
cam.release()
GPIO.cleanup()
