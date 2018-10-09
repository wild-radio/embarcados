import threading
import os
import RPi.GPIO as GPIO
import numpy as np
import cv2
from time import sleep

sensor = False
timed_photo = False

class Motors:
    def __init__(self, out1, out2):
        # initialize
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(out1, GPIO.OUT)  # 0o3
        GPIO.setup(out2, GPIO.OUT)  # 0o5
        # setup frequency
        self.pwm1 = GPIO.PWM(out1, 50)
        self.pwm2 = GPIO.PWM(out2, 50)

        # starts with 0% duty cycle
        self.pwm1.start(0)
        self.pwm2.start(0)

    # changes servo 1 angle
    def set_angle1(self, angle):
        duty = int(angle) / 18 + 2
        GPIO.output(0o3, True)
        self.pwm1.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(0o3, False)
        self.pwm1.ChangeDutyCycle(0)

    # changes servo 2 angle
    def set_angle2(self, angle):
        duty = int(angle) / 18 + 2
        GPIO.output(0o5, True)
        self.pwm2.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(0o5, False)
        self.pwm2.ChangeDutyCycle(0)


class FileMonitor(threading.Thread):
    def __init__(self, nome_do_arquivo):
        self.nome = nome_do_arquivo
        if os.path.exists(self.nome):
            self.last_modified = os.path.getmtime(self.nome)
        else:
            self.last_modified = None
        threading.Thread.__init__(self)

    def run(self):
        global sensor
        while True:
            if os.path.exists(self.nome) and os.path.getmtime(self.nome) != self.last_modified:
                self.last_modified = os.path.getmtime(self.nome)
                print('%s modified' % self.nome)
                f = open(self.nome, "r")
                lines = f.read().splitlines()
                print lines
                Motors.set_angle1(lines[0])
                Motors.set_angle2(lines[1])
                sleep(2)
                sensor = True
                f.close()


class Camera(threading.Thread):
    def __init__(self, cam):
        self.cam = cv2.VideoCapture(cam)  # starts cam capturing
        self.img_counter = 0  # picture_name counter
        threading.Thread.__init__(self)

    def run(self):
        global sensor
        global timed_photo
        while True:
            if sensor or timed_photo:
                frame = self.cam.read()[1]
                img_name = "opencv_frame_{}.png".format(self.img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                self.img_counter += 1
                sensor = False
                timed_photo = False


archive_monitor = FileMonitor("arquivo.txt")
archive_monitor.start()
file_monitor = FileMonitor("file.txt")
file_monitor.start()
camera_thread = Camera(0)
camera_thread.start()
motors_cam1 = Motors(0o3, 0o5)
