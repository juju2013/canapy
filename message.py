#! /usr/bin/env python

import struct
import utils
import binascii
import autopy

KEY_CTRL = 0;
KEY_SHFT = 1;
KEY_ALT = 2;
KEY_CMD = 4;

MOUSE_BTN1 = 0;
MOUSE_BTN2 = 1;
MOUSE_BTN3 = 2;

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
	def __init__(self,btn, btn2):
		self.ucbtn=btn
		self.apbtn=btn2

	def ifclick(self, msg):
		newstate=((msg[2]&self.ucbtn)==self.ucbtn)
		if self.state != newstate:
			self.state=newstate
			autopy.mouse.toggle(newstate, self.apbtn)

	def btnstat(self,btn):
		if btn: return "down"
		return "up"

class msgMouse(ucmsg):
	id='\x10\x10'
	btn1=msgBtn(0b0001, autopy.mouse.LEFT_BUTTON)
	btn2=msgBtn(0b0010, autopy.mouse.CENTER_BUTTON)
	btn3=msgBtn(0b0100, autopy.mouse.RIGHT_BUTTON)

	def response(self): 
		dx,dy=self.detail()
		if dx*dy !=0 :
			x,y=autopy.mouse.get_pos()
			try: autopy.mouse.move(mx(x,dx), my(y,dy))
			except: 
				print "cannot move to p(%s,%s)"%(x+dx, y+dy)
				pass
		self.btn1.ifclick(self.msg)
		self.btn2.ifclick(self.msg)
		self.btn3.ifclick(self.msg)

	def detail(self):
		dx=normalize(struct.unpack("!i", self.msg[4:8])[0])
		dy=normalize(struct.unpack("!i", self.msg[8:12])[0])
		dw=normalize(struct.unpack("!i", self.msg[12:16])[0])
		return (dx,dy)

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
def mx(x, dx): return min(max(x+dx, 0), autopy.screen.get_size()[0])
def my(x, dx): return min(max(x+dx, 0), autopy.screen.get_size()[1])
