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
    height=160, 
    rotation=90, 
    spi_speed_hz=4000000
)

font_size = 8

while True:
    # 建立畫布並繪製內容
    img = Image.new('RGB', (160, 128), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    my_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
        font_size
    ) 

    draw.text((10, 10), f"{font_size}pt: Hello Raspberry Pi!", fill=(255, 255, 255), font=my_font)

    # 顯示影像
    disp.display(img)
    sleep(0.5)

    font_size += 1
    if font_size > 16:
        font_size = 8
