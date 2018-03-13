# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
import sys
import time
import datetime
from gpiozero import MCP3208
import os
import dht11

# 初期設定
map_data = list()
map_node = list()

# map_dataからmapの情報取得
f = open('map_data.txt', 'r')
for line in f:
	map_data.append(line[:-1])
f.close()

# mapの横、縦の長さ取得
map_width = max([len(x) for x in map_data])
map_height = len(map_data)
#print map_width
#print map_height

# 温湿度センサの設定
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
instance = dht11.DHT11(pin = 21)

# 照度、水センサーのch指定
# 取り付けてないいとエラー吐かれるのでセンサ取り付けるまではコメアウト推奨
light1 = MCP3208(channel = 0)
light2 = MCP3208(channel = 2)
sen_water = MCP3208(channel = 7)


# nodeの生成 動かしたいプログラムの中にnode作らんとセンサデータ送れないから
# これで作ってや
# 戻り値：map_node
def node_create():
	global map_data
	print "node_create"

	map_node = list()
	createtime = datetime.datetime.today()
	map_bunkatu = [[mp for mp in line] for line in map_data]
	map_node = [[[0 for mx in range(1)] for my in range(map_width)] for mz in range(map_height)]

	for cx in range(map_height):
		for cy in range(map_width):

			# ノードが通れるかどうか判定(state)
			if str(map_bunkatu[cx][cy]) in ' ':
				inputstate = str('True')
			elif str(map_bunkatu[cx][cy]) in '0':
				inputstate = str('false')

			map_node[cx][cy] = {"state":inputstate, "light":None, "water":None, "humidity": None, "temperatur":None, "time":createtime}

	#print map_node		#めっちゃ出るよ
	print "node_create finish"

	return map_node

# mapの障害物状況を表示
def mapview():
	f = open('map_data.txt', 'r')
	for line in f:
		map_data.append(line[:-1])
		print line,
	f.close()



# map_node内のデータを書き込む
# 出力；node_data.txt
def data_write(map_node):
		writedata = open('node_data.txt', 'w')
		for hx in range(map_height):
			for hy in range(map_width):

				# state
				if map_node[hx][hy]["state"] == None:
					st = "None "
				else:
					st = str(map_node[hx][hy]["state"]) + " "
				# light
				if map_node[hx][hy]["light"] ==None:
					li = "None "
				else:
					li = str(map_node[hx][hy]["light"]) + " "
				# water
				if map_node[hx][hy]["water"] ==None:
					wa = "None "
				else:
					wa = str(map_node[hx][hy]["water"]) + " "
				# humidity
				if map_node[hx][hy]["humidity"] ==None:
					hu = "None "
				else:
					hu = str(map_node[hx][hy]["humidity"]) + " "
				# temperatur
				if map_node[hx][hy]["temperatur"] ==None:
					te = "None "
				else:
					te = str(map_node[hx][hy]["light"]) + " "
				# time
				if map_node[hx][hy]["time"] ==None:
					ti = "None\n"
				else:
					ti = str(map_node[hx][hy]["time"]) + "\n"

				s = str(hx) + " " + str(hy) + " " + st + li + wa + hu + te + ti
				#print s,	#debug
				writedata.write(s)
		writedata.close()


# （受け取った）データを読み込む
# inputdata.txt自体はDatap2p.pyの中で作ってる
# これ実行した後はdata_write()実行するのがおススメ
def data_read(map_node):
	if not os.path.exists("./inputdata.txt"):
		print "inputdata.txtがありません"
		return 0

	read = open('inputdata.txt', 'r')
	line2 = read.readlines()
	read.close()

	for line in line2:
		line = line.split()
		#print line		#debug

		# データが入ってないなら更新せず
		if 'None' in line:
			continue
		else:
			x = int(line[0])
			y = int(line[1])
			sta = line[2]
			lig = line[3]
			wat = line[4]
			hum = line[5]
			tem = line[6]
			tim = line[7] + " " + line[8]

			# 受け取ったデータが新しい物で、データが存在するなら更新する
			if tim > str(map_node[x][y]["time"]):
				map_node[x][y]["state"] = sta
				map_node[x][y]["light"] = lig
				map_node[x][y]["water"] = wat
				map_node[x][y]["humidity"] = hum
				map_node[x][y]["temperatur"] = tem
				map_node[x][y]["time"] = tim

			#print map_node[x][y]

# センサーの値を読み込んでmap_node内のそれぞれにぶち込む
# 引数：情報格納ノードmap_node(), 現在位置 mx, my
def sensor_read(map_node, mx, my):
	global light1, light2, sen_water, instance
	thresult = instance.read()

	# 照度センサ 二つの平均を照度として用いる
	l1 = light1.value
	l2 = light2.value
	l = (l1 + l2) / 2

	# よし、じゃあ(map_nodeに)ぶち込んでやるぜ
	map_node[mx][my]["light"] = l							# 照度
	map_node[mx][my]["water"] = sen_water.value				# 土壌水分
	map_node[mx][my]["humidity"] = thresult.humidity		# 温度
	map_node[mx][my]["temperatur"] = thresult.temperature	# 湿度
	map_node[mx][my]["time"] = datetime.datetime.today()	# 時間

# map_node内に入ってるデータを表示させる
def data_show(map_node):
	# ヘッダー
	print "=============================================================================================="

	for dx in range(map_height):
		print "| dx | dy | state |  light   |  water   | humidity | temperatur |        cleatetime          |"
		print "|----|----|-------|----------|----------|----------|------------|----------------------------|"

		for dy in range(map_width):

			"""
			# ノードが通れるかどうか判定
			if str(map_data[dx][dy]) in ' ':
				map_node[dx][dy]["state"] = 'True'
			if str(map_data[dx][dy]) in '0':
				map_node[dx][dy]["state"] = 'false'

			# 時間にがNoneなら作成時間挿入
			if map_node[dx][dy]["time"] == None:
				map_node[dx][dy]["time"] = datetime.datetime.today()

			if map_node[dx][dy]["state"] == None:
				temp_state = 'None'
			else:
				temp_state = str(map_node[dx][dy]["state"])

			if map_node[dx][dy]["light"] == None:
				temp_light = 'None'
			else:
				temp_light = str(map_node[dx][dy]["light"])

			if map_node[dx][dy]["water"] == None:
				temp_water = 'None'
			else:
				temp_water = str(map_node[dx][dy]["water"])

			if map_node[dx][dy]["humidity"] == None:
				temp_humidity = 'None'
			else:
				temp_humidity = str(map_node[dx][dy]["humidity"])

			if map_node[dx][dy]["temperatur"] == None:
				temp_temperatur = 'None'
			else:
				temp_temperatur = str(map_node[dx][dy]["temperatur"])
			"""

			# 表示調整用の変数に各パラメータ記入
			# センサ類の値は少数第五桁まで四捨五入してます
			temp_state = map_node[dx][dy]["state"]

			if map_node[dx][dy]["light"] != None:
				temp_light = round(float(map_node[dx][dy]["light"]), 5)
				temp_water = round(float(map_node[dx][dy]["water"]), 5)
				temp_humidity = round(float(map_node[dx][dy]["humidity"]), 5)
				temp_temperatur = round(float(map_node[dx][dy]["temperatur"]), 5)

			else:
				temp_light = "None"
				temp_water = "None"
				temp_humidity = "None"
				temp_temperatur = "None"

			# 表示位置調整
			show_state 		= str(temp_state)	   + (" " * (5 - len(str(temp_state))))
			show_light 		= str(temp_light)	   + (" " * (8 - len(str(temp_light))))
			show_water 		= str(temp_water)	   + (" " * (8 - len(str(temp_water))))
			show_humidity 	= str(temp_humidity)   + (" " * (8 - len(str(temp_humidity))))
			show_temperatur = str(temp_temperatur) + (" " * (10 - len(str(temp_temperatur))))

			# 表示
			print "| %2d | %2d"%(dx, dy),
			print "| {0}".format(show_state),
			print "| {0}".format(show_light),
			print "| {0}".format(show_water),
			print "| {0}".format(show_humidity),
			print "| {0}".format(show_temperatur),
			print "| {0} |".format(map_node[dx][dy]["time"])
		# フッター
		print "|============================================================================================|"

"""
try:
	global map_node
	while True:
		data_show()
		#data_read()
		#data_write()

		while True:
			sensor_read()
			data_read()
			data_show()

			print "dx,dy?"
			p = input()
			print "light water? humidity? temperatur?write?(頭文字)"
			mode = raw_input()
			print "number?"
			changenum = input()

			print p, str(mode), changenum

			if mode in ['light', 'l']:
				map_node[p[0]][p[1]]["light"] = changenum
			elif mode in ['water', 'w']:
				map_node[p[0]][p[1]]["water"] = changenum
			elif mode in ['humidity', 'h']:
				map_node[p[0]][p[1]]["humidity"] = changenum
			elif mode in ['temperatur', 't']:
				map_node[p[0]][p[1]]["temperatur"] = changenum
			elif mode in ['write']:
				data_write()

			else:
				print "なんかおかしいぞ"
				sys.exit(1)
			if mode not in ['write']:
				map_node[p[0]][p[1]]["time"] = datetime.datetime.today()

except KeyboardInterrupt:
	print "\n一時中断\n"
	sys.exit(1)

"""