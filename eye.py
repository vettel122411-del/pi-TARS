from PIL import Image

import numpy as np
from copy import deepcopy

from os import makedirs

img = np.array(Image.open("105724566.png")).astype(np.float16)

print(img.shape)

BIAS_Y = 17
BIAS_X = 23
SIZE = 45

for y in range(img.shape[0]):
    for x in range(img.shape[1]):
        r, g, b, a = img[y][x]
        if r+b-g > (r+g+b)/3*1.5:
            img[y][x] = [255, 255, 255, 255]
        else:
            img[y][x] = [0, 0, 0, 0]

eye_left = [deepcopy(img[y:y+SIZE, x:x+SIZE]) for y in range(BIAS_Y, img.shape[0]-SIZE, SIZE) for x in range(BIAS_X, img.shape[1]-SIZE, SIZE)]
eye_right = [deepcopy(im[:, ::-1]) for im in eye_left]



DIR = "eye_check"
makedirs(DIR, exist_ok=True)

for i, eye in enumerate( zip(eye_left, eye_right) ):
    img_eye = np.concatenate(eye, axis=1)
    Image.fromarray(img_eye.astype(np.uint8)).save(f"{DIR}/110_eye_{i}.png")

for y in range(BIAS_Y, img.shape[0], SIZE):
    for x in range(img.shape[1]):
        img[y][x] = [255, 0, 0, 255]

for x in range(BIAS_X, img.shape[1], SIZE):
    for y in range(img.shape[0]):
        img[y][x] = [255, 0, 0, 255]
    
Image.fromarray(img.astype(np.uint8)).save(f"{DIR}/110_mask.png")