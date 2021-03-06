import threading
import os
import RPi.GPIO as GPIO
import numpy as np
import cv2
from time import sleep
import time
import subprocess


class Motors:
    def __init__(self, out1, out2):
        # initialize
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(out1, GPIO.OUT)
        GPIO.setup(out2, GPIO.OUT)
        self.pin1 = out1
        self.pin2 = out2
        self.pwm1 = GPIO.PWM(out1, 50)  # setup frequency
        self.pwm2 = GPIO.PWM(out2, 50)  # setup frequency
        self.pwm1.start(0)  # starts with 0% duty cycle
        self.pwm2.start(0)  # starts with 0% duty cycle

    # changes servo 1 angle
    def set_angle1(self, angle):
        angle = int(angle) * -1
        if angle < -60 or angle > 60:
            return

        duty = (90 + angle) / 18.0 + 2
        GPIO.output(self.pin1, True)
        self.pwm1.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.pin1, False)
        self.pwm1.ChangeDutyCycle(0)

    # changes servo 2 angle
    def set_angle2(self, angle):
        angle = int(angle) * -1
        if angle < -60 or angle > 60:
            return

        duty = (90 + angle) / 18.0 + 2
        GPIO.output(self.pin2, True)
        self.pwm2.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.pin2, False)
        self.pwm2.ChangeDutyCycle(0)


class FileMonitor(threading.Thread):
    def __init__(self, file_name):
        self.file_name = file_name
        global motors_cam1
        global motors_cam2
        global cam1
        global cam2
        self.pri_ang1 = None
        self.pri_ang2 = None
        self.alt_ang1 = None
        self.alt_ang2 = None
        if os.path.exists(self.file_name):
            self.last_modified = os.path.getmtime(self.file_name)
            f = open(self.file_name, "r")
            lines = f.read().splitlines()
            print lines
            if self.file_name == "/home/pi/.wildradio/config/principal.txt":
                cam1.active = (lines[0] == '1')  # type: bool
                cam1.periodic = (lines[1] == '1')  # type: bool
                cam1.sensor_flag = False  # type: bool
                self.pri_ang1 = lines[3]
                self.pri_ang2 = lines[4]
                motors_cam1.set_angle1(lines[3])
                sleep(1)
                motors_cam1.set_angle2(lines[4])
                cam1.sensor_flag = (lines[2] == '1')  # type: bool
            elif self.file_name == "/home/pi/.wildradio/config/alternativa.txt":
                cam2.active = (lines[0] == '1')  # type: bool
                cam2.periodic = (lines[1] == '1')  # type: bool
                cam2.sensor_flag = False  # type: bool
                if int(lines[3]) > 40:
                    lines[3] = '40'
                elif int(lines[3]) < -40:
                    lines[3] = '-40'
                if int(lines[4]) > 40:
                    lines[4] = '40'
                elif int(lines[4]) < -40:
                    lines[4] = '-40'
                self.alt_ang1 = lines[3]
                self.alt_ang2 = lines[4]
                motors_cam2.set_angle1(lines[3])
                sleep(1)
                motors_cam2.set_angle2(lines[4])
                cam2.sensor_flag = (lines[2] == '1')  # type: bool
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
                if self.file_name == "/home/pi/.wildradio/config/principal.txt":
                    cam1.active = (lines[0] == '1')  # type: bool
                    cam1.periodic = (lines[1] == '1')  # type: bool
                    cam1.sensor_flag = False  # type: bool
                    if self.pri_ang1 != lines[3]:
                        self.pri_ang1 = lines[3]
                        motors_cam1.set_angle1(lines[3])
                        sleep(1)
                    if self.pri_ang2 != lines[4]:
                        self.pri_ang2 = lines[4]
                        motors_cam1.set_angle2(lines[4])
                    if lines[5] == '1':
                        sleep(0.3)
                        cam1.take_picture("/home/pi/.wildradio/pictures/main/confirmation_cam_1.ppm")
                    cam1.sensor_flag = (lines[2] == '1')  # type: bool
                elif self.file_name == "/home/pi/.wildradio/config/alternativa.txt":
                    cam2.active = (lines[0] == '1')  # type: bool
                    cam2.periodic = (lines[1] == '1')  # type: bool
                    cam2.sensor_flag = False  # type: bool
                    if int(lines[3]) > 40:
                        lines[3] = '40'
                    elif int(lines[3]) < -40:
                        lines[3] = '-40'
                    if int(lines[4]) > 40:
                        lines[4] = '40'
                    elif int(lines[4]) < -40:
                        lines[4] = '-40'
                    if self.alt_ang1 != lines[3]:
                        self.alt_ang1 = lines[3]
                        motors_cam2.set_angle1(lines[3])
                        sleep(1)
                    if self.alt_ang2 != lines[4]:
                        self.alt_ang2 = lines[4]
                        motors_cam2.set_angle2(lines[4])
                    if lines[5] == '1':
                        sleep(0.3)
                        cam2.take_picture("/home/pi/.wildradio/pictures/secondary/confirmation_cam_2.ppm")
                    cam2.sensor_flag = (lines[2] == '1')  # type: bool
                f.close()
            sleep(0.5)


class Camera(threading.Thread):
    def __init__(self, cam, folder):
        self.cam = cv2.VideoCapture(cam)  # starts cam capturing
        self.cam_folder = folder  # cam number to img name
        self.active = False
        self.periodic = False
        self.timer_flag = False
        self.sensor_flag = False
        self.frame = None
        self.timed_photo()
        threading.Thread.__init__(self)

    def run(self):
        global sensor_cam1
        global sensor_cam2
        while True:
            if self.active:
                if (self.cam_folder == "main" and sensor_cam1 and self.sensor_flag) or (
                        self.cam_folder == "secondary" and sensor_cam2 and self.sensor_flag) or (
                        self.periodic and self.timer_flag):
                    img_name = "/home/pi/.wildradio/pictures/{}/{}.ppm".format(self.cam_folder, int(time.time()))
                    self.take_picture(img_name)
                    self.timer_flag = False
                    if self.cam_folder == "main":
                        sensor_cam1 = False
                    elif self.cam_folder == "secondary":
                        sensor_cam2 = False
                else:
                    self.timer_flag = False
            sleep(0.05)

    def take_picture(self, img_name):
        if self.cam.isOpened():
            for i in range(10):
                self.frame = self.cam.grab()
            im = self.cam.read()[1]
            print im
            if im is not None:
                img = cv2.resize(im, (320, 240))
                cv2.imwrite(img_name, img)
                print("{} written!".format(img_name))

    def timed_photo(self):
        if self.periodic:
            self.timer_flag = True
        print "{} timer".format(self.cam_folder)
        threading.Timer(600, self.timed_photo).start()


def get_cams_ids():
    lsusb = subprocess.check_output(["lsusb"])
    ls_dev = subprocess.check_output(["ls", "/dev"])
    cam1_dev = None
    cam2_dev = None
    cam1_index = None
    cam2_index = None
    dev_ids = []

    for line in ls_dev.splitlines():
        if "video" in line:
            dev_ids.append(int(line[-1]))

    dev_ids.sort()

    for line in lsusb.splitlines():
        words = line.split()
        if words[6] == 'Z-Star':
            cam1_dev = int(words[3].replace(":", ""))
        elif words[6] == 'GEMBIRD':
            cam2_dev = int(words[3].replace(":", ""))

    if cam1_dev and cam2_dev and cam1_dev > cam2_dev:
        cam1_index = dev_ids[1]
        cam2_index = dev_ids[0]
    elif cam1_dev and cam2_dev and cam1_dev < cam2_dev:
        cam1_index = dev_ids[0]
        cam2_index = dev_ids[1]
    elif cam1_dev:
        cam1_index = 0
    elif cam2_dev:
        cam2_index = 0

    print "cam1 index = {}".format(cam1_index)
    print "cam1 dev = {}".format(cam1_dev)
    print "cam2 index = {}".format(cam2_index)
    print "cam2 dev = {}".format(cam2_dev)
    return [cam1_index, cam2_index]


motors_cam1 = Motors(35, 33)
motors_cam2 = Motors(38, 36)
sensor_pin = 7
GPIO.setup(sensor_pin, GPIO.IN)
GPIO.add_event_detect(sensor_pin, GPIO.RISING)
sensor_cam1 = False
sensor_cam2 = False
cam1_id, cam2_id = get_cams_ids()
cam1 = Camera(cam1_id, "main")
if not cam1.cam.isOpened():
    print "cam1 nao conectada"
else:
    cam1.start()
cam2 = Camera(cam2_id, "secondary")
if not cam2.cam.isOpened():
    print "cam2 nao conectada"
else:
    cam2.start()
file_monitor1 = FileMonitor("/home/pi/.wildradio/config/principal.txt")
file_monitor1.start()
file_monitor2 = FileMonitor("/home/pi/.wildradio/config/alternativa.txt")
file_monitor2.start()
try:
    while True:
        if GPIO.event_detected(sensor_pin):
            sleep(0.3)
            sensor_cam1 = True
            sensor_cam2 = True
        sleep(0.05)
except KeyboardInterrupt:
    cam1.cam.release()
    cam2.cam.release()
    exit(1)
