#! /usr/bin/env python

import socket, time
import binascii
from threading import Thread
import utils
import message

class daemon(Thread):
	def __init__(self):
		#utils.Borg.__init__(self)
		Thread.__init__(self, target=self.run)
		self.hostname=socket.gethostname()
		self.eq=utils.exitQueue()
		self.daemon=True

class responder(daemon):
	def __init__(self):
		daemon.__init__(self)
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(("0.0.0.0",13894))
		self.start()

	def run(self):
		print "responder started"		
		while not self.eq.stop:
			try:
				data,client=self.socket.recvfrom(1024)
				if not data: continue
				if len(data)<2: continue
				if data[0:2] != '\x01\x01': continue
				m=message.msgBrdResponse(self.hostname)
				self.socket.sendto(m.msg, client)
			except: time.sleep(1)
		print "responder stopped"
		self.socket.close()


class dispatcher(daemon):
	def __init__(self):
		daemon.__init__(self)
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(("0.0.0.0",13894))
		self.start()

	def run(self):
		print "dispatcher started"
		self.socket.listen(1)
		while not self.eq.stop:
			conn,addr=self.socket.accept()
			tcphandler(conn,addr)
		print "dispatcher stopped"
		self.socket.close()


class tcphandler(daemon):
	def __init__(self, socket, addr):
		daemon.__init__(self)
		self.socket=socket
		self.addr=addr
		self.socket.sendall(message.msgConfirm().response())
		self.start()

	def run(self):
		print "tcp handler started"
		while not self.eq.stop:
			#try:
				data=self.socket.recv(32)
				if not data: break
				if len(data) < 1: break
				if len(data)<32: continue
				m = message.getMsg(data)
				#if isinstance(m, message.msgMouse):
				#	dx,dy=m.detail()
				#	if dx*dy != 0:
				#	if m.msg[2] != 32:
				#		print "btns %s"%m.msg[2]
				r = m.response()
				if r:
					self.socket.sendall(m.response())
			#except: pass
		print "tcp handler stopped"
		self.socket.close()


