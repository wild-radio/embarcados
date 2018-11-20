import subprocess

lsusb = subprocess.check_output(["lsusb"])
cam1_dev = None
cam2_dev = None
cam1_index = None
cam2_index = None

for line in lsusb.splitlines():
    words = line.split()
    if words[6] == 'Z-Star':
        cam1_dev = int(words[3].replace(":", ""))
    elif words[6] == 'GEMBIRD':
        cam2_dev = int(words[3].replace(":", ""))

if cam1_dev and cam2_dev and cam1_dev > cam2_dev:
    cam1_index = 1
    cam2_index = 0
elif cam1_dev and cam2_dev and cam1_dev < cam2_dev:
    cam1_index = 0
    cam2_index = 1

print "cam1 index = {}".format(cam1_index)
print "cam1 dev = {}".format(cam1_dev)
print "cam2 index = {}".format(cam2_index)
print "cam2 dev = {}".format(cam2_dev)