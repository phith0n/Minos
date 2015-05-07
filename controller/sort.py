#coding=utf-8
__author__ = 'phithon'
import tornado.web
from controller.base import BaseHandler
from tornado import gen
import pymongo
from bson.objectid import ObjectId
from util.function import time_span, intval

class SortHandler(BaseHandler):
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		sortid = args[0]
		limit = 15
		page = intval(args[2])
		if not page or page <= 0 : page = 1
		sort = yield self.db.sort.find_one({
			"_id": ObjectId(sortid)
		})
		if not sort:
			self.custom_error("板块不存在")
		cursor = self.db.article.find({
			"sort._id": ObjectId(sortid)
		})
		count = yield cursor.count()
		cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		posts = yield cursor.to_list(length = limit)
		self.render("sort.htm", posts = posts, page = page, sort = sort, time_span = time_span,
			count = count, each = limit)