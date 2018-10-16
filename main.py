import threading
import os
import RPi.GPIO as GPIO
import numpy as np
import cv2
from time import sleep
import time


class Motors:
    def __init__(self, out1, out2):
        # initialize
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(out1, GPIO.OUT)
        GPIO.setup(out2, GPIO.OUT)
        self.pin1 = out1
        self.pin2 = out2
        self.pwm1 = GPIO.PWM(out1, 50) # setup frequency
        self.pwm2 = GPIO.PWM(out2, 50) # setup frequency
        self.pwm1.start(0) # starts with 0% duty cycle
        self.pwm2.start(0) # starts with 0% duty cycle

    # changes servo 1 angle
    def set_angle1(self, angle):
        if angle < -60 or angle > 60:
            return

        duty = (90 + int(angle)) / 18 + 2
        GPIO.output(self.pin1, True)
        self.pwm1.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.pin1, False)
        self.pwm1.ChangeDutyCycle(0)

    # changes servo 2 angle
    def set_angle2(self, angle):
        if angle < -60 or angle > 60:
            return

        duty = (90 + int(angle)) / 18 + 2
        GPIO.output(self.pin2, True)
        self.pwm2.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.pin2, False)
        self.pwm2.ChangeDutyCycle(0)


class FileMonitor(threading.Thread):
    def __init__(self, file_name):
        self.file_name = file_name
        if os.path.exists(self.file_name):
            self.last_modified = os.path.getmtime(self.file_name)
            f = open(self.file_name, "r")
            lines = f.read().splitlines()
            print lines
            if self.file_name == "~/.wildradio/config/principal.txt":
                cam1.active = (lines[0] == 1)  # type: bool
                cam1.periodic = (lines[1] == 1)  # type: bool
                cam1.sensor_flag = (lines[2] == 1)  # type: bool
                motors_cam1.set_angle1(lines[3])
                motors_cam1.set_angle2(lines[4])
            elif self.file_name == "~/.wildradio/config/alternativa.txt":
                cam2.active = (lines[0] == 1)  # type: bool
                cam2.periodic = (lines[1] == 1)  # type: bool
                cam2.sensor_flag = (lines[2] == 1)  # type: bool
                motors_cam2.set_angle1(lines[3])
                motors_cam2.set_angle2(lines[4])
            f.close()
        else:
            self.last_modified = None
        threading.Thread.__init__(self)

    def run(self):
        global motors_cam1
        global motors_cam2
        global cam1
        global cam2
        while True:
            if os.path.exists(self.file_name) and os.path.getmtime(self.file_name) != self.last_modified:
                self.last_modified = os.path.getmtime(self.file_name)
                print('%s modified' % self.file_name)
                f = open(self.file_name, "r")
                lines = f.read().splitlines()
                print lines
                if self.file_name == "~/.wildradio/config/principal.txt":
                    cam1.active = (lines[0] == 1)  # type: bool
                    cam1.periodic = (lines[1] == 1)  # type: bool
                    cam1.sensor_flag = (lines[2] == 1)  # type: bool
                    motors_cam1.set_angle1(lines[3])
                    motors_cam1.set_angle2(lines[4])
                    if lines[5] == 1:
                        cam1.take_picture("~/.wildradio/pictures/confirmation_cam_1")
                elif self.file_name == "~/.wildradio/config/alternativa.txt":
                    cam2.active = (lines[0] == 1)   # type: bool
                    cam2.periodic = (lines[1] == 1)  # type: bool
                    cam2.sensor_flag = (lines[2] == 1)  # type: bool
                    motors_cam2.set_angle1(lines[3])
                    motors_cam2.set_angle2(lines[4])
                    if lines[5] == 1:
                        cam2.take_picture("~/.wildradio/pictures/confirmation_cam_2")
                f.close()


class Camera(threading.Thread):
    def __init__(self, cam, index, sensor_pin):
        self.cam = cv2.VideoCapture(cam)  # starts cam capturing
        self.cam_index = index            # cam number to img name
        self.sensor_pin = sensor_pin
        self.active = False
        self.periodic = False
        self.timer_flag = False
        self.sensor_flag = False
        GPIO.setup(self.sensor_pin, GPIO.IN)
        GPIO.add_event_detect(self.sensor_pin, GPIO.RISING)
        self.timed_photo()
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if self.active:
                if (GPIO.event_detected(self.sensor_pin) and self.sensor_flag) or (self.periodic and self.timer_flag):
                    img_name = "cam{}_{}.png".format(self.cam_index, time.time())
                    self.take_picture(img_name)
                else:
                    self.timer_flag = False

    def take_picture(self, img_name):
        frame = self.cam.read()[1]
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))

    def timed_photo(self):
        if self.periodic:
            self.timer_flag = True
        threading.Timer(60, self.timed_photo).start()


motors_cam1 = Motors(40, 37)
motors_cam2 = Motors(38, 35)
cam1 = Camera(0, 1, 3)
cam1.start()
cam2 = Camera(1, 2, 3)
cam2.start()
file_monitor1 = FileMonitor("~/.wildradio/config/principal.txt")
file_monitor1.start()
file_monitor2 = FileMonitor("~/.wildradio/config/alternativa.txt")
file_monitor2.start()
