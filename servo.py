import threading
import os
import RPi.GPIO as GPIO
from time import sleep


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
        if int(angle) < -60 or int(angle) > 60:
            return

        duty = (90 + int(angle)) / 18 + 2
        GPIO.output(self.pin1, True)
        self.pwm1.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.pin1, False)
        self.pwm1.ChangeDutyCycle(0)

    # changes servo 2 angle
    def set_angle2(self, angle):
        if int(angle) < -60 or int(angle) > 60:
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
        global motors_cam1
        global motors_cam2
        if os.path.exists(self.file_name):
            self.last_modified = os.path.getmtime(self.file_name)
            f = open(self.file_name, "r")
            lines = f.read().splitlines()
            print lines
            if self.file_name == "/home/pi/.wildradio/config/principal.txt":
                motors_cam1.set_angle1(lines[3])
                motors_cam1.set_angle2(lines[4])
            elif self.file_name == "/home/pi/.wildradio/config/alternativa.txt":
                motors_cam2.set_angle1(lines[3])
                motors_cam2.set_angle2(lines[4])
            f.close()
        else:
            self.last_modified = None
        threading.Thread.__init__(self)

    def run(self):
        global motors_cam1
        global motors_cam2
        while True:
            if os.path.exists(self.file_name) and os.path.getmtime(self.file_name) != self.last_modified:
                self.last_modified = os.path.getmtime(self.file_name)
                print('%s modified' % self.file_name)
                f = open(self.file_name, "r")
                lines = f.read().splitlines()
                print lines
                if self.file_name == "/home/pi/.wildradio/config/principal.txt":
                    motors_cam1.set_angle1(lines[3])
                    motors_cam1.set_angle2(lines[4])
                elif self.file_name == "/home/pi/.wildradio/config/alternativa.txt":
                    motors_cam2.set_angle1(lines[3])
                    motors_cam2.set_angle2(lines[4])
                f.close()
            sleep(0.5)


motors_cam1 = Motors(35, 33)
motors_cam2 = Motors(38, 36)
file_monitor1 = FileMonitor("/home/pi/.wildradio/config/principal.txt")
file_monitor1.start()
file_monitor2 = FileMonitor("/home/pi/.wildradio/config/alternativa.txt")
file_monitor2.start()

while True:
    sleep(0.1)
