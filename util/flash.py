__author__ = 'phithon'

class flash(dict):
	def __init__(self, request):
		dict.__init__(self)
		self.request = request

	def __getitem__(self, item):
		item = "flash_%s" % item
		if item in self.request.session:
			value = self.request.session.get(item)
			self.request.session.delete(item)
		else:
			value = ""
		return value

	def get(self, k, d = None):
		return self.__getitem__(k)

	def __delattr__(self, item):
		item = "flash_%s" % item
		self.request.session.delete(item)

	def __setitem__(self, key, value):
		key = "flash_%s" % key
		self.request.session[key] = value