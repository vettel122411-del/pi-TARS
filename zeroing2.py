from adafruit_servokit import ServoKit
from time import sleep

import json

import sys

with open("config.json") as fp:
	config = json.load(fp)

pca = ServoKit(channels=16)

for i in range(2):
	pca.servo[i].set_pulse_width_range(config["range"][i]["lo"], (config["range"][i]["hi"]))


pca.servo[0].angle = 180-config["move"][0]["A0"]
pca.servo[1].angle = config["move"][1]["A0"]
sleep(0.5)

if len(sys.argv) >= 2 and sys.argv[1]=="zeroing":
	exit(0)

sleep(1.0)

while True:
	pca.servo[0].angle = 180 -config["move"][0]["A0"] - config["move"][0]["A1"]
	pca.servo[1].angle = config["move"][1]["A0"] + config["move"][1]["A1"]
	sleep(0.6)

	if len(sys.argv) >= 2 and sys.argv[1]=="forward":
		exit(0)

	for da in range(config["misc"]["splits"], 0, -1):
		ratio = da/config["misc"]["splits"]
		pca.servo[0].angle = 180-config["move"][0]["A0"] - ratio*config["move"][0]["A1"]
		pca.servo[1].angle = config["move"][1]["A0"] + ratio*config["move"][1]["A1"]
		sleep(5e-3)
	
	sleep(0.4)
	
