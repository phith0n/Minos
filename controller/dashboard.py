#coding=utf-8
import tornado.web, re
from controller.base import BaseHandler
from tornado import gen
import time, pymongo
from util.function import intval
from bson.objectid import ObjectId

class AdminHandler(BaseHandler):
	def initialize(self):
		super(AdminHandler, self).initialize()
		self.topbar = "admin"

	def prepare(self):
		super(AdminHandler, self).prepare()
		if self.power != "admin":
			self.redirect("/")

	def render(self, template_name, **kwargs):
		if self.power == "admin":
			render = "admin/%s" % template_name
		else:
			render = template_name
		super(AdminHandler, self).render(render, **kwargs)

	def get(self, *args, **kwargs):
		action = args[0] if len(args) else "index"
		method = "_view_%s" % action
		arg = args[2] if len(args) == 3 else None
		if hasattr(self, method):
			getattr(self, method)(arg)
		else:
			self._view_index(arg)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_index(self, arg):
		user = self.db.member.find()
		article = self.db.article.find()
		sort = self.db.sort.find()
		active = self.db.member.find({
			"logintime": {"$gt": time.time() - 3 * 24 * 60 * 60}
		})
		count = {
			"user": (yield user.count()),
			"article": (yield article.count()),
			"sort": (yield sort.count()),
			"active": (yield active.count())
		}
		user.sort([('time', pymongo.DESCENDING)]).limit(10)
		newusers = yield user.to_list(10)
		self.render("index.htm", count = count, newusers = newusers)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_user(self, arg):
		username = self.get_query_argument("username", default=None)
		where = {"username": {"$regex": ".*"+re.escape(username)+".*"}} if username else {}
		limit = 15
		page = intval(arg)
		page = page if page > 1 else 1
		user = self.db.member.find(where)
		count = yield user.count()
		user.sort([('time', pymongo.ASCENDING)]).limit(limit).skip((page - 1) * limit)
		users = yield user.to_list(limit)
		if username:
			search = "?username=%s" % username
		else:
			search = ""
		self.render("userlist.htm", page = page, users = users, count = count, each = limit, search = search)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_userdetail(self, arg):
		username = arg
		user = yield self.db.member.find_one({
			"username": username
		})
		if not user:
			self.custom_error("不存在这个用户")
		self.render("userdetail.htm", user = user)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_sort(self, arg):
		limit = 15
		page = intval(arg)
		page = page if page > 1 else 1
		cursor = self.db.sort.find()
		count = yield cursor.count()
		cursor.limit(limit).skip((page - 1) * limit)
		sorts = yield cursor.to_list(limit)
		self.render("sort.htm", sorts = sorts, count = count, each = limit, page = page)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_sortdetail(self, arg):
		id = arg
		sort = yield self.db.sort.find_one({
			"_id": ObjectId(id)
		})
		if not sort:
			self.custom_error("不存在这个板块")
		self.render("sortdetail.htm", sort = sort)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_setting(self, arg):
		site = self.settings.get("site")
		init_money = self.settings.get("init_money")
		captcha = self.settings.get("captcha")
		register = self.settings.get("register")
		self.render("setting.htm", site = site, init_money = init_money, captcha = captcha, register = register)

	@tornado.web.asynchronous
	@gen.coroutine
	def _view_invite(self, arg):
		where = self.get_query_argument("act", default=None)
		act = {
			"nouse": {"used": False},
			"used": {"used": True},
			"expire": {
				"time": {"$lt": time.time() - self.settings["invite_expire"]},
				"used": False
			}
		}
		where = act.get(where) if (where in act) else {}
		limit = 15
		page = intval(arg)
		page = page if page > 1 else 1
		cursor = self.db.invite.find(where)
		count = yield cursor.count()
		cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		invites = yield cursor.to_list(limit)
		self.render("invite.htm", invites = invites, count = count, each = limit, page = page)
