#coding=utf-8
__author__ = 'phithon'
import tornado.web
from controller.base import BaseHandler
from tornado import gen
import pymongo, re
from bson.objectid import ObjectId
from util.function import time_span, intval

def cutstr(content):
	return content[0:30] + "..."

class MessageHandler(BaseHandler):
	def initialize(self):
		BaseHandler.initialize(self)
		self.topbar = "message"

	def post(self, *args, **kwargs):
		method = self.get_body_argument("method", default=None)
		if method and hasattr(self, "_%s_action" % method):
			getattr(self, "_%s_action" % method)()
		else:
			self.custom_error("不存在这个方法")

	@tornado.web.asynchronous
	@gen.coroutine
	def _readall_action(self):
		yield self.db.message.update({
			"to": self.current_user["username"],
			"read": False
		}, {
			"$set": {"read": True}
		}, multi = True)
		self.redirect("/message")

	@tornado.web.asynchronous
	@gen.coroutine
	def _deleteall_action(self):
		yield self.db.message.remove({
			"to": self.current_user["username"]
		}, multi = True)
		self.redirect("/message")

	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		limit = 20
		page = intval(args[1])
		if not page or page <= 0 : page = 1
		cursor = self.db.message.find({
			"$or": [
				{"to": self.current_user["username"]},
				{"from": self.current_user["username"]}
			]
		})
		count = yield cursor.count()
		cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		messages = yield cursor.to_list(length = limit)
		self.render("message.htm", messages = messages, count = count, cutstr = cutstr)

class DetailHandler(BaseHandler):

	def initialize(self):
		BaseHandler.initialize(self)
		self.topbar = "message"

	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		id = args[0]
		message = yield self.db.message.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$set": {"read": True}
		})
		self.render("msgdetail.htm", message = message)