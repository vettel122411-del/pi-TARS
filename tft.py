from eye import eye_left, eye_right
import numpy as np
import random

import st7735
from PIL import Image, ImageDraw, ImageFont
from gpiozero import DigitalOutputDevice

from time import sleep

# 初始化 GPIO 18 為輸出裝置
backlight = DigitalOutputDevice(18)

# 打開背光
backlight.on()

# 關閉背光
# backlight.off()

# 初始化顯示器 (對應上述接線)
# port=0, device=0 代表使用 /dev/spidev0.0
disp = st7735.ST7735(
    port=0, 
    cs=0, 
    dc=24, 
    rst=25, 
    width=132, 
    height=162, 
    # rotation=90, 
    rotation=0,
    spi_speed_hz=4000000,
    invert=False
)


def genEye(eyes):
    e = random.choice(eyes)
    while True:
        if random.random() < 0.3:
            e = random.choice(eyes)
            for _ in range(9):
                yield e

        yield e

gen_left = genEye(eye_left)
gen_right = genEye(eye_right)


while True:
    for i, eye in enumerate( zip(eye_left, eye_right) ):
        img = np.zeros((128, 180, 4), dtype=np.float16)
        
        y0 = img.shape[0]//2 - next(gen_left).shape[0]//2
        x0 = img.shape[1]//2 - next(gen_left).shape[1]//2 - 20
        e = next(gen_left)
        img[y0:y0+e.shape[0], x0:x0+e.shape[1]] = e.astype(np.float16)

        x0 = img.shape[1]//2 + 20
        e = next(gen_right)
        img[y0:y0+e.shape[0], x0:x0+e.shape[1]] = e.astype(np.float16)

        disp.display(Image.fromarray(np.transpose(img.clip(0, 255).astype(np.uint8), (1, 0, 2))[::-1,:, :3]))
        sleep(1/60)


# while True:
#     font_size = 8
    
#     # 建立畫布並繪製內容
#     img = Image.new('RGB', (160, 128), color=(0, 0, 0))
#     draw = ImageDraw.Draw(img)

#     my_font = ImageFont.truetype(
#         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
#         font_size
#     ) 

#     draw.text((10, 10), f"{font_size}pt: Hello Raspberry Pi!", fill=(255, 255, 255), font=my_font)

#     # 顯示影像
#     disp.display(img)
#     sleep(0.5)

#     font_size += 1
#     if font_size > 16:
#         font_size = 8
