#coding=utf-8
__author__ = 'phithon'
import tornado.web
from controller.base import BaseHandler
from tornado import gen
import pymongo
from bson.objectid import ObjectId
from util.function import time_span, intval

class HomeHandler(BaseHandler):
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		limit = 15
		page = intval(args[1])
		if not page or page <= 0 : page = 1
		cursor = self.db.article.find()
		cursor.sort([('top', pymongo.DESCENDING), ("lastcomment", pymongo.DESCENDING), ('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		count = yield cursor.count()
		posts = yield cursor.to_list(length = limit)
		sorts = yield self.get_sort()
		self.render("main.htm", posts = posts, sorts = sorts, page = page,
					time_span = time_span, count = count, each = limit)

	@gen.coroutine
	def get_sort(self):
		sorts = []
		cursor = self.db.sort.find({
			"show": True
		})
		while (yield cursor.fetch_next):
			sorts.append(cursor.next_object())
		raise gen.Return(sorts)