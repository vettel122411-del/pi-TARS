from adafruit_servokit import ServoKit
from time import sleep

import json

import sys

import redis


with open("config.json") as fp:
	config = json.load(fp)

r = redis.Redis(host='localhost', port=6379, db=0)
r.delete("commands")

pca = ServoKit(channels=16)

for i in range(2):
	pca.servo[i].set_pulse_width_range(config["range"][i]["lo"], (config["range"][i]["hi"]))


def zeroing():
	sleep(0.001)
	pca.servo[0].angle = 180-config["move"][0]["A0"]
	pca.servo[1].angle = config["move"][1]["A0"]

def move(rate_left, rate_right, hold=0.4):
	pca.servo[0].angle = 180-config["move"][0]["A0"] - config["move"][0]["A1"]
	pca.servo[1].angle = config["move"][1]["A0"] + config["move"][1]["A1"]
	sleep(hold)

	for s in range(config["misc"]["splits"]+1):
		ratio = s/config["misc"]["splits"]
		pca.servo[0].angle = 180-config["move"][0]["A0"] - max(1-rate_left,1-ratio)*config["move"][0]["A1"]
		pca.servo[1].angle = config["move"][1]["A0"] + max(1-rate_right,1-ratio)*config["move"][1]["A1"]
		sleep(5e-3)

	sleep(0.1)

def move_forward():
	move(1.0, 1.0)

def turn_left(level=0.5):
	move(1-level, 1, 0.75)

def turn_right(level=0.5):
	move(1, 1-level, 0.75)


zeroing()
sleep(0.5)

while True:
	zeroing()

	c = r.lpop("commands")
	if c:
		c = c.decode("utf-8")
		print(c)

		if c == "stop":
			zeroing()
			r.delete("commands")
		elif c == "forward":
			move_forward()
		elif c == "turn_left":
			turn_left()
		elif c == "turn_right":
			turn_right()
		elif c == "quit":
			break

		if len(r.lrange("commands", 0, -1)) == 0:
			if c != "stop":
				r.rpush("commands", c)

	zeroing()
