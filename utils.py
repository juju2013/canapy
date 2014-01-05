#! /usr/bin/env python
import Queue

# simple singleton/monostate
class Borg(object):
  stop=False
  _shared_state = {}
  def __init__(self):
    self.__dict__ = self._shared_state


class exitQueue(Borg):
	def __init__(self):
		Borg.__init__(self)
		if not self.__dict__.has_key('_queue') : self._queue=Queue.Queue(100)

	def exit(self):
		print "interrupted..."
		self.stop=True
		for i in range(self._queue.maxsize):
			try:
				self._queue.put_nowait(true)
			except:
				break
				