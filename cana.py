#! /usr/bin/env python

import sys, os, signal
import time
from utils import *
import responder
  

class main:
	def __init__(self):
		self.exitQ=exitQueue()
		signal.signal(signal.SIGINT, stopMe)
		self.responder=responder.responder()
		self.dispatcher=responder.dispatcher()

def stopMe(signum, frame):
	exitQueue().exit()

if __name__ == "__main__":
  m=main()
  eq=exitQueue()
  while not eq.stop: time.sleep(5000)
