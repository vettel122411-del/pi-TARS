from adafruit_servokit import ServoKit
from time import sleep

import json

with open("config.json") as fp:
	config = json.load(fp)

pca = ServoKit(channels=16)

for i in range(2):
	pca.servo[i].set_pulse_width_range(config["range"][i]["lo"], (config["range"][i]["hi"]))


pca.servo[0].angle = 180
pca.servo[1].angle = 0
sleep(2)

exit(0)

while True:
	pca.servo[0].angle = 180-35
	pca.servo[1].angle = 35
	sleep(0.9)
	
	
	for da in range(35*5, 0, -1):
		pca.servo[0].angle = 180-da/5
		pca.servo[1].angle = da/5
		sleep(5e-3)
	
	sleep(1)
	
