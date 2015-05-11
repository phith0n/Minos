#coding=utf-8
__author__ = 'phithon'
import tornado.web, time
from controller.base import BaseHandler
from tornado import gen
from bson.objectid import ObjectId
from util.function import time_span, intval

class AjaxHandler(BaseHandler):
	def get(self, *args, **kwargs):
		self.json("fail", "no action!")

	def post(self, *args, **kwargs):
		action = "_%s_action" % args[0]
		if hasattr(self, action):
			getattr(self, action)()
		else:
			self.json("fail", "no action!")

	@tornado.web.asynchronous
	@gen.coroutine
	def _like_action(self):
		id = self.get_body_argument("post")
		post = yield self.db.article.find_one({
			"_id": ObjectId(id)
		})
		if not post:
			self.json("fail", "post id error")
		self.__check_already(post)
		post["like"].append(self.current_user["username"])
		yield self.db.article.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$set": {"like": post["like"]}
		})
		self.json("success", len(post["like"]))

	@tornado.web.asynchronous
	@gen.coroutine
	def _unlike_action(self):
		id = self.get_body_argument("post")
		post = yield self.db.article.find_one({
			"_id": ObjectId(id)
		})
		if not post:
			self.json("fail", "post id error")
		self.__check_already(post)
		post["unlike"].append(self.current_user["username"])
		yield self.db.article.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$set": {"unlike": post["unlike"]}
		})
		self.json("success", len(post["unlike"]))

	@tornado.web.asynchronous
	@gen.coroutine
	def _bookmark_action(self):
		id = self.get_body_argument("post")
		post = yield self.db.article.find_one({
			"_id": ObjectId(id)
		})
		if not post:
			self.json("fail", "article not found")
		user = yield self.db.member.find_one({
			"username": self.current_user["username"]
		})
		for row in user["bookmark"]:
			if id == row["id"]:
				self.json("fail", "already bookmark")
		bookmark = {
			"id": str(post["_id"]),
			"title": post["title"],
			"user": post["user"],
			"sort": post["sort"],
			"time": time.time()
		}
		ret = yield self.db.member.update({
			"username": self.current_user["username"]
		}, {
			"$push": {"bookmark": bookmark}
		})
		self.json("success", "done")

	@tornado.web.asynchronous
	@gen.coroutine
	def _thanks_action(self):
		id = self.get_body_argument("id")
		if not id:
			self.json("fail", "post not exists!")
		post = yield self.db.article.find_one({
			"_id": ObjectId(id),
			"thanks": {"$nin": [self.current_user["username"]]}
		})
		if not post:
			self.json("fail", "already thanks")
		if post["user"] == self.current_user["username"]:
			self.json("fail", "cannot thanks to yourself")
		old = yield self.db.member.find_and_modify({
			"username": self.current_user["username"],
			"money": {"$gt": 0}
		}, {
			"$inc": {"money": -1}
		})
		if not old:
			self.json("fail", "money not enough")
		yield self.db.member.find_and_modify({
			"username": post["user"]
		}, {
			"$inc": {"money": 1}
		})
		yield self.db.article.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$push": {"thanks": self.current_user["username"]}
		})
		yield self.message(fromuser = None, touser = post["user"],
						   content = u"你的文章《%s》被%s感谢了" % (post["title"], self.current_user["username"]),
						   jump="/post/%s" % id)
		self.clear_cookie("flush_info")
		self.json("success", "thanks success")

	@tornado.web.asynchronous
	@gen.coroutine
	def _newmsg_action(self):
		cursor = self.db.message.find({
			"$and": [
				{"read": False},
				{"$or": [
					{"to": self.current_user["username"]},
					{"from": self.current_user["username"]}
				]},
			]
		})
		count = yield cursor.count()
		self.json("success", count)

	def __check_already(self, post):
		'''
		检查like、unlike是否重复

		:param post:
		:return:
		'''
		if (self.current_user["username"] in post["unlike"]):
			self.json("fail", "already unliked")
		if (self.current_user["username"] in post["like"]):
			self.json("fail", "already liked")

	def json(self, status, info):
		self.write({
			"status": status,
			"info": info
		})
		raise tornado.web.Finish()