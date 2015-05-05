import tornado.web
from controller.base import BaseHandler

class MainHandler(BaseHandler):
	def get(self):
		self.write("Hello, world")