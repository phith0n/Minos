#coding=utf-8
__author__ = 'phithon'
import tornado.web
from controller.base import BaseHandler
from tornado import gen
import time, pymongo, os, uuid
from bson.objectid import ObjectId
from util.function import random_str, hash, intval
from model.user import UserModel
from model.sort import SortModel

class AdminHandler(BaseHandler):
	def initialize(self):
		super(AdminHandler, self).initialize()
		self.topbar = "admin"

	def prepare(self):
		super(AdminHandler, self).prepare()
		if self.power != "admin":
			self.redirect("/")

	def post(self, *args, **kwargs):
		method = ("%s_action" % args[0]) if len(args) > 0 else "home_action"
		if hasattr(self, method):
			getattr(self, method)(*args, **kwargs)
		else:
			self.home_action(*args, **kwargs)

	@tornado.web.asynchronous
	@gen.coroutine
	def register_action(self, *args, **kwargs):
		method = self.get_body_argument("method", default=None)
		if method in ["open", "close", "invite"]:
			config = self._read_config()
			config["global"]["register"] = method
			self._write_config(config)
			self.flash["register"] = "设置成功"
		else:
			self.flash["register"] = "注册方法不正确"
		self.redirect("/admin/")

	@tornado.web.asynchronous
	@gen.coroutine
	def invite_action(self, *args, **kwargs):
		action = self.get_body_argument("action")
		if action == "create":
			code = random_str()
			try:
				yield self.db.invite.insert({
					"code": code,
					"used": False,
					"user": "",
					"time": time.time()
				})
			except pymongo.errors.DuplicateKeyError:
				pass
			self.redirect("/manage/invite")
		elif action == "delete":
			code = self.get_body_argument("code")
			yield self.db.invite.remove({
				"code": code,
				"used": False
			})
			self.redirect("/manage/invite")
		elif action == "expire":
			yield self.db.invite.remove({
				"time": {"$lt": (time.time() - self.settings["invite_expire"])},
				"used": {"$eq": False}
			})
			self.redirect("/manage/invite")
		self.custom_error("方法错误，请重试")

	@tornado.web.asynchronous
	@gen.coroutine
	def article_action(self, *args, **kwargs):
		method = self.get_body_argument("method", default="")
		id = self.get_body_argument("id", default=None)
		if method in ("star", "unstar"):
			star = True if method == "star" else False
			post = yield self.db.article.find_and_modify({
				"_id": ObjectId(id)
			}, {
				"$set": {
					"star": star
				}
			})
			content = u"你的文章《%s》被管理员" % post["title"] + (u"加精" if star else u"取消精华") + u"了"
			yield self.message(fromuser=None, touser=post["user"], content=content,
							   jump="/post/%s" % id)
		elif method in ("open", "close"):
			open = True if method == "open" else False
			post = yield self.db.article.find_and_modify({
				"_id": ObjectId(id)
			}, {
				"$set": {
					"open": open
				}
			})
		elif method in ("top", "notop"):
			top = True if method == "top" else False
			post = yield self.db.article.find_and_modify({
				"_id": ObjectId(id)
			}, {
				"$set": {
					"top": top
				}
			})
			yield self.message(fromuser=None, touser=post["user"], jump="/post/%s" % id,
				content=u"你的文章《%s》被管理员%s了" % (post["title"], u"置顶" if top else u"取消置顶"))
		elif method == "del":
			post = yield self.db.article.find_and_modify({
				"_id": ObjectId(id)
			}, remove = True)
			if not post:
				self.custom_error("不存在这篇文章", jump="/")
			yield self.db.member.update({
			}, {
				"$pull": {
					"bookmark": {"id": id}
				}
			}, multi = True)
			yield self.message(fromuser=None, touser=post["user"], jump="/post/%s" % id,
				content=u"你的文章《%s》被管理员删除了" % post["title"])
			self.redirect("/")
		elif method == "rank":
			rank = intval(self.get_body_argument("rank"))
			post = yield self.db.article.find_one({
				"_id": ObjectId(id)
			})
			if not post:
				self.custom_error("不存在这篇文章")
			if "rank" in post and post.get("rank") != 0:
				self.custom_error("已经评分过啦")
			if not (-10 <= rank <= 10):
				self.custom_error("评分超出范围拉")
			yield self.db.member.find_and_modify({
				"username": post["user"]
			}, {
				"$inc": {"money": rank}
			})
			yield self.db.article.find_and_modify({
				"_id": ObjectId(id)
			}, {
				"$set": {"rank": rank}
			})
			yield self.message(fromuser=None, touser=post["user"],
				content=u"你的文章《%s》被管理员" % post["title"] + (u"奖励" if rank > 0 else u"扣除") + u"%d金币" % abs(rank),
				jump="/post/%s" % id)

		self.redirect("/post/%s" % id)

	@tornado.web.asynchronous
	@gen.coroutine
	def delcomment_action(self, *args, **kwargs):
		comid = self.get_body_argument("comid")
		postid = self.get_body_argument("postid")
		yield self.db.article.find_and_modify({
			"_id": ObjectId(postid),
		}, {"$pull": {
				"comment": {
					"_id": {"$eq": ObjectId(comid)}
				}
			}
		})
		self.redirect("/post/%s" % postid)

	@tornado.web.asynchronous
	@gen.coroutine
	def edituser_action(self, *args, **kwargs):
		id = self.get_body_argument("id")
		user = dict(
			money = intval(self.get_body_argument("money")),
			power = intval(self.get_body_argument("power")),
			email = self.get_body_argument("email"),
			website = self.get_body_argument("website"),
			qq = self.get_body_argument("qq"),
			address = self.get_body_argument("address"),
			signal = self.get_body_argument("signal"),
		)
		model = UserModel()
		if not model(user):
			self.custom_error(model.error_msg)
		password = self.get_body_argument("password", default=None)
		if password:
			user["password"] = yield self.backend.submit(hash.get, password)
		user = yield self.db.member.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$set": user
		})
		self.redirect("/manage/userdetail/%s" % user['username'])

	@tornado.web.asynchronous
	@gen.coroutine
	def sort_action(self, *args, **kwargs):
		id = self.get_body_argument("id")
		sort = dict(
			name = self.get_body_argument("name"),
			intro = self.get_body_argument("intro",default=None),
			show = True if intval(self.get_body_argument("show", default=None)) else False
		)
		model = SortModel()
		if not model(sort):
			self.custom_error(model.error_msg)
		sort = yield self.db.sort.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$set": sort
		})
		if not sort:
			self.custom_error("不存在这个板块")
		else:
			self.redirect("/manage/sortdetail/%s" % id)

	@tornado.web.asynchronous
	@gen.coroutine
	def setting_action(self, *args, **kwargs):
		config = self._read_config()
		config["global"]["site"] = dict(
			webname = self.get_body_argument("webname"),
			keyword = self.get_body_argument("keyword"),
			description = self.get_body_argument("description")
		)
		config["global"]["init_money"] = intval(self.get_body_argument("init_money"))
		config["global"]["register"] = self.get_body_argument("register")
		if config["global"]["register"] not in ("open", "invite", "close"):
			self.custom_error("注册方法不正确")
		captcha = self.get_body_arguments("captcha")
		for d in ("register", "login", "comment"):
			config["global"]["captcha"][d] = True if (d in captcha) else False
		key = self.get_body_argument("key", default=None)
		if key:
			config["global"]["cookie_secret"] = key
		self._write_config(config)
		self.redirect("/manage/setting")
