# Author: Iqbal Mohomed
# Notice: This code is provided as is - no warranties
#
# For details on the project, see my personal blog: slowping.com
# This is a personal project done on my own time. 
#
# 
# Python version: 2.6
# Libraries used: pyBrain, nxt-python (v2.2.1), PIL (Python Image Libary)
#
# This code has been used successfully on Windows 7. 
# On Mac OS X (Snow Leopard), the SynchronizedMotors class has given me some grief.
#
# Initially, I've placed all my code into this file. I hope to clean it up as I get time.
#
# Have fun!!

import nxt
import sys
import time
from msvcrt import *
from PIL import Image
import urllib
import pickle

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

net = buildNetwork(10000,64,3,bias=True)
ds = SupervisedDataSet(10000,3)
f = open('training.txt','r')
st=f.readlines()
print len(st)

def save_net(nnet,fname):
	fileOb = open(fname,'w')
	pickle.dump(nnet, fileOb)
	fileOb.close()

def load_net(fname):
	fileOb = open(fname,'r');
	nnet = pickle.load(fileOb);
	fileOb.close();
	nnet.sorted = False
	nnet.sortModules()
	return nnet;

def use_nnet(nnet,im):
	cmd = ''
	lst = list(im.getdata())
	res=nnet.activate(lst)
	val = res.argmax()
	if val == 0:
		cmd = 'f'
	elif val == 1:
		cmd = 'l'
	elif val == 2:
		cmd = 'r'
	return cmd

def exec_cmd(cmd):
	if cmd == 'f':
		go(m,250)
	elif cmd == 'b':
		back(m,250)
	elif cmd == 'l':
		go(mls,250)
	elif cmd == 'r':
		go(mrs,250)
	elif cmd == 'x':
		b.sock.close()

def auto(nnet):
	while True:
		im=take_pic()
		cmd=use_nnet(nnet,im)
		exec_cmd(cmd)
		print "executing .." + cmd
		time.sleep(3)

def initBrick():
	global b
	global r
	global l
	global m
	global mls
	global mrs
	b = nxt.find_one_brick()
	r = nxt.Motor(b, nxt.PORT_A)
	l = nxt.Motor(b, nxt.PORT_B)
	# create synchronized motors
	m = nxt.SynchronizedMotors(r,l, 0)
	mls = nxt.SynchronizedMotors(l, r, 20)
	mrs = nxt.SynchronizedMotors(r, l, 20)

def makevec(val):
	res = [0]*9
	res[val] = 1
	return res

def findOne(lst):
	r=0
	while r < len(lst):
		if lst[r] == 1:
			return r
		r+=1
	print 'Error in findOne()'
	return -1;


def train(net,ds,p=100):
	trainer = BackpropTrainer(net,ds)
	trainer.trainUntilConvergence(maxEpochs=p)
	return trainer

def makeds_cross(st,ds,n, N):
	L = len(st)
	P = L/N
	start = P * n
	i = 0
	while i < L:
		if (i > start) and (i < (start + P)):
			i += 1
			continue
                inp = map(int,st[i].split()[0:-3])
                ou = map(int,st[i].split()[-3:])
                ds.addSample(inp,ou)
		i+=1

def run_cross(st,net,n,N):
        correct = 0
        L = len(st)
	P = L/N
	start = P * n
	total = 0
	j = start
        while j< (start + P):
                t = st[j].split()[0:-3]
                t2 = map(int,t)
                a = st[j].split()[-3:]
                a2 = map(int,a)
                j+=1
		total +=1
                guess = net.activate(t2)
                if guess.argmax() == findOne(a2):
                        correct += 1
        print str(correct) + " " + str(total)

def makeds(st,ds):
	i=0
	L = len(st)
	while i < L:
		inp = map(int,st[i].split()[0:-3])
		ou = map(int,st[i].split()[-3:])
		ds.addSample(inp,ou)
		i+=1

def run(st,net):
	correct = 0
	j=0
	L = len(st)
	while j< L:
		t = st[j].split()[0:-3]
		t2 = map(int,t)
		a = st[j].split()[-3:]
		a2 = map(int,a)
		j+=1
		guess = net.activate(t2)
		if guess.argmax() == findOne(a2):
			correct += 1
	print str(correct) + " " + str(L)


def download_image(theurl):
	urllib.urlretrieve(theurl)

def take_pic():
	res=urllib.urlretrieve('http://192.168.1.12:8080/shot.jpg')
	im = Image.open(res[0])
	nim = im.convert('L')
	nim2=nim.resize((100,100))
	return nim2;

def trainer():
	while True:
		im=take_pic() # download pic and read it to a file
		cmd = accept_execute_cmd()
		record_data(im,cmd) #photo and cmd

def cmd2arr(cmd):
	res = [0] * 3;
	if cmd == 'f':
		res[0] = 1;
	elif cmd == 'l':
		res[1] = 1;
	elif cmd == 'r':
		res[2] = 1;
	return res;

def makestr(lst):
	res = ""
	for i in lst:
		res += str(i) + " "
	return res;

def record_data(im,cmd):
	# read photo.jpg and make it into array
	lst = list(im.getdata())
	cmdarr = cmd2arr(cmd)
	lst.extend(cmdarr)
	f = open('training.txt','a')
	st=makestr(lst)
	f.write(st + '\r\n')
	f.close()



#b = nxt.find_one_brick()
#r = nxt.Motor(b, nxt.PORT_A)
#l = nxt.Motor(b, nxt.PORT_B)

# create motors
#m = nxt.SynchronizedMotors(r,l, 0)
#ml = nxt.SynchronizedMotors(l, r, 6)
#mls = nxt.SynchronizedMotors(l, r, 20)
#mr = nxt.SynchronizedMotors(r, l, 6)
#mrs = nxt.SynchronizedMotors(r, l, 20)
#mll = nxt.SynchronizedMotors(l,r,100)
#mrr = nxt.SynchronizedMotors(r, l,100)
	
def go(dev,amt):
	dev.turn(100,amt);

def back(dev,amt):
	dev.turn(-100,amt);


def accept_execute_cmd():
	cmd = '';
	gotCmd = False;
	print "CMD: "
	while gotCmd == False:
		cmd = getch();
		#cmd = raw_input('CMD: ')
		if cmd == 'f':
			go(m,250)
			gotCmd = True;
		elif cmd == 'b':
			back(m,250)
			gotCmd = True;
		elif cmd == 'l':
			go(mls,250)
			gotCmd = True;
		elif cmd == 'r':
			go(mrs,250)
			gotCmd = True;
		elif cmd == 'R':
			go(mrr,71)
			gotCmd = True;
		elif cmd == 'L':
			go(mll,71)
			gotCmd = True;
		elif cmd == 'x':
			b.sock.close()
			gotCmd = False;
			exit();
	print cmd + "\n";
	return cmd;

###############################################################
# The following sections are meant to be exclusive. 
# Comment one of the sections to acheive your desired function.
###############################################################

# To get Training samples, uncomment below
#print "Loaded"
#initBrick();
#trainer();

# For self-drive, uncomment below
#initBrick();
#auto(net);

# To train neuralnet, uncomment below 
#makeds(st,ds)
#train(net,ds,500)
#save_net(net,'net20_500.dat')
