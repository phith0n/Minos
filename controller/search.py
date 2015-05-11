#coding=utf-8
__author__ = 'phithon'
import tornado.web
from controller.base import BaseHandler
from tornado import gen
import pymongo, re
from bson.objectid import ObjectId
from util.function import time_span, intval

class SearchHandler(BaseHandler):
	def initialize(self):
		BaseHandler.initialize(self)
		self.topbar = ""

	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		keyword = self.get_query_argument("keyword", default=None)
		if not keyword:
			self.custom_error("关键词不能为空")
		esp_keyword = re.escape(keyword)
		limit = 20
		page = intval(args[1])
		if not page or page <= 0 : page = 1
		cursor = self.db.article.find({
			"title": {"$regex": ".*%s.*" % esp_keyword, "$options": "i"}
		})
		count = yield cursor.count()
		cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		posts = yield cursor.to_list(length = limit)
		self.render("search.htm", posts = posts, page = page, keyword = keyword,
					time_span = time_span, count = count, each = limit)