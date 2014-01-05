#! /usr/bin/env python

import struct
import utils
import binascii

import pymouse

KEY_CTRL = 0;
KEY_SHFT = 1;
KEY_ALT = 2;
KEY_CMD = 4;

MOUSE_BTN1 = 0;
MOUSE_BTN2 = 1;
MOUSE_BTN3 = 2;
pm=pymouse.PyMouse()

class ucmsg(object):
	id=None
	msg=bytearray(b'\x00'*32)
	def __init__(self):
		struct.pack_into("!2s", self.msg, 0, self.id)

	def response(self):
		return self.msg

	def toStr(self): return binascii.hexlify(self.msg)

class msgBrdRequest(ucmsg):
	id='\x01\x01'

class msgConfirm(ucmsg):
	id='\x04\x04'

class msgBrdResponse(ucmsg):
	id='\x02\x02'
	def __init__(self, name="localhost", version=126):
		ucmsg.__init__(self)
		struct.pack_into('!16s',self.msg,16,name)
		struct.pack_into('b',self.msg,3,4)
		struct.pack_into('b',self.msg,4,3)

class msgAgentInfoResponse(ucmsg):
	id='\x21\x21'
	def response(self):
		struct.pack_into('b',self.msg,3,4)
		struct.pack_into('b',self.msg,4,3)
		return self.msg

class msgBtn:
	state=False
	def __init__(self,btn, idx):
		self.ucbtn=btn
		self.idx=idx

	def click(self, msg):
		newstate=((msg[2]&self.ucbtn)==self.ucbtn)
		if self.state != newstate:
			self.state=newstate
			x,y=pm.position()
			if newstate: pm.press(x,y, self.idx)
			else: pm.release(x,y,self.idx)
			self.state=newstate

btns=[msgBtn(0b0001, 1), msgBtn(0b0010, 3), msgBtn(0b0100, 2)]
lastScroll=0

class msgMouse(ucmsg):
	id='\x10\x10'

	def response(self):
		dx,dy, dw=self.detail()
		if dx*dy !=0 :
			x,y=pm.position()
			pm.move(x+dx, y+dy)
		for b in btns: b.click(self.msg)
		pm.scroll(vertical=dw)

	def detail(self):
		dx=normalize(struct.unpack("!i", self.msg[4:8])[0])
		dy=normalize(struct.unpack("!i", self.msg[8:12])[0])
		dw=normalize(struct.unpack("!i", self.msg[12:16])[0]/4)
		if dw != 0:
			global lastScroll
			if dw != lastScroll:
				dw=dw/abs(dw)
				lastScroll=dw
			else: dw=0
		return (dx,dy, dw)


class msgAgentInfo(ucmsg):
	id='\x20\x20'
	def response(self):
		return msgAgentInfoResponse().response()

def getMsg(msg):
	id=msg[0]
	for x in ucmsg.__subclasses__():
		if x.id == struct.pack('cc',id,id): 
			m=x()
			m.msg[:]=msg
			return x();
	m=ucmsg()
	m.msg[:]=msg
	print "todo:%s"%binascii.hexlify(id)
	return m

def normalize(i): return max(min(i,100),-100)
