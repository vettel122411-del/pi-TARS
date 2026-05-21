from adafruit_servokit import ServoKit
from time import sleep

import json

import sys

with open("config.json") as fp:
	config = json.load(fp)

pca = ServoKit(channels=16)

for i in range(2):
	pca.servo[i].set_pulse_width_range(config["range"][i]["lo"], (config["range"][i]["hi"]))


def zeroing():
	pca.servo[0].angle = 180-config["move"][0]["A0"]
	pca.servo[1].angle = config["move"][1]["A0"]

def move_forward():
	pca.servo[0].angle = 180-config["move"][0]["A0"] - config["move"][0]["A1"]
	pca.servo[1].angle = config["move"][1]["A0"] + config["move"][1]["A1"]
	sleep(0.4)

	for da in range(config["misc"]["splits"], 0, -1):
		ratio = da/config["misc"]["splits"]
		pca.servo[0].angle = 180-config["move"][0]["A0"] - ratio*config["move"][0]["A1"]
		pca.servo[1].angle = config["move"][1]["A0"] + ratio*config["move"][1]["A1"]
		sleep(5e-3)

	sleep(0.3)



zeroing()
sleep(0.5)

while True:
	move_forward()


	
