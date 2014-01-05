#! /usr/bin/env python

from socket import *
import utils

class broadcaster:
	eq=utils.exitQueue()

	def __init__(self):
		self.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.id=socket.gethostname()