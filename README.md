# pi-TARS

這是一專題製作，專題的內容是一個tars機器人，這一專題一共分成三版:


## hi
+ **第一版**是先預測空間 排線 主要功能和下一版需要改編的項目
+ **第二版**是解決第一版無法改善的項目和功能重心和關節穩定性等


第二版的語音識別上遇到了一點困難是vosk的使用狀況不穩定，找不到想要說的話。所以我們換了一個sherpa-onnx但是這個
模型需要比較好的性能才跑的順暢，所以我們有去超頻到2G，在設定 over_voltage=6 後，電壓通常會提升至約 1.0V 到 1.04V 之間。，還需解局散熱問題。

---

第二版再組裝壓克力板的時候遇到了廠商製造失誤，所以所做成品跟設計上有所差別。還遇到摩擦地不夠在原地走路，所以我們加了橡皮筋

第二版在調整動態平衡上面需要微調，因問一隻腳較長需要墊一些紙，再去調整他的動態平衡。

在螢幕上我們找了一張眼睛原圖片，然後去做去背，用座標定位去做切割眼睛的範圍，再讓他去隨機的去撥放眼睛
![eye_image](./105724566.png)

我們要去連結走路和語音識別的程式上我們用了docker來啟動redis服務，在 Redis 中，List（列表） 是一個雙向鏈結串列（Doubly Linked List）。它的特點是左右兩端插入與彈出速度極快，且元素允許重複並依插入順序排序。語音識別後的指令是RPUSH，但是停止指令適用LPUSH，讓它放在指令的最前面(插隊)。
```python

while True:
	zeroing()

	k,c = r.blpop("commands")
	c = c.decode("utf-8")

	print(c)

	if c == "quit":
		break
	
	elif c == "stop":
		zeroing()
		r.delete("commands")
	
	else:
		if c == "forward":
			move_forward()
		elif c == "turn_left":
			turn_left()
		elif c == "turn_right":
			turn_right()
```
在WALK裡取出是BLPOP從左邊拿指令，停止先歸零再把所有未執行指令再刪除，

```python
if len(r.lrange("commands", 0, -1)) == 0:
	r.lpush("commands", c)
```
如果現在List是空的就會把最後的指令重新加回去List裡

