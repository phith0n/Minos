#coding=utf-8
__author__ = 'phithon'
import tornado.web, os, base64, pymongo, time
from controller.base import BaseHandler
from tornado import gen
from bson.objectid import ObjectId
from util.function import time_span, hash, intval
from model.user import UserModel

class UserHandler(BaseHandler):
	def initialize(self):
		super(UserHandler, self).initialize()
		self.topbar = ""

	def get(self, *args, **kwargs):
		method = "%s_act" % args[0]
		if len(args) == 3 : arg = args[2]
		else: arg = None
		if hasattr(self, method):
			getattr(self, method)(arg)
		else:
			self.detail_act()

	def quit_act(self, arg):
		if self.get_cookie("user_info"):
			self.clear_cookie("user_info")
		if self.get_cookie("download_key"):
			self.clear_cookie("download_key")
		self.session.delete("current_user")
		self.redirect("/login")

	@tornado.web.asynchronous
	@gen.coroutine
	def modify_act(self, arg):
		pass

	@tornado.web.asynchronous
	@gen.coroutine
	def detail_act(self, arg):
		if not arg : arg = self.current_user["username"]
		username = self.get_query_argument("u", default = arg)
		user = yield self.db.member.find_one({
			"username": username
		})
		if not user:
			self.custom_error("不存在这个用户")

		limit = 10
		page = intval(self.get_argument("page", default=1))
		if not page or page <= 0 : page = 1
		cursor = self.db.article.find({
			"user": username
		})
		count = yield cursor.count()
		cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		posts = yield cursor.to_list(length = limit)
		face = "./static/face/%s/180.png" % user["_id"]
		if not os.path.exists(face): face = "./static/face/guest.png"
		self.render("user.htm", user = user, posts = posts, page = page, time_span = time_span, each = limit, count = count)

	@tornado.web.asynchronous
	@gen.coroutine
	def edit_act(self, arg):
		user = yield self.db.member.find_one({
			"username": self.current_user["username"]
		})
		self.render("profile.htm", user = user, radio = self.radio)

	def face_act(self, arg):
		self.render("face.htm")

	@tornado.web.asynchronous
	@gen.coroutine
	def bookmark_act(self, arg):
		limit = 10
		page = intval(arg)
		if page <= 0 : page = 1
		user = yield self.db.member.find_one({
			"username": self.current_user["username"]
		})
		bookmark = user.get("bookmark")
		count = len(bookmark)
		bookmark = bookmark[(page - 1) * limit:(page - 1) * limit + limit]
		bookmark.reverse()
		self.render("bookmark.htm", bookmark = bookmark, page = page, count = count, each = limit)

	@tornado.web.asynchronous
	@gen.coroutine
	def like_act(self, arg):
		limit = 10
		page = intval(arg)
		if page <= 0 : page = 1
		cursor = self.db.article.find({
			"like": self.current_user["username"]
		})
		count = yield cursor.count()
		cursor.sort([('_id', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		posts = yield cursor.to_list(length = limit)
		self.render("like.htm", posts = posts, page = page, count = count, each = limit)


	@tornado.web.asynchronous
	@gen.coroutine
	def download_act(self):
		key = self.get_query_argument("key")
		task = yield self.db.task.find_one({
			"_id": ObjectId(key),
			"owner": self.current_user.get("username")
		})
		if task and os.path.exists(task["savepath"]):
			self.set_secure_cookie("download_key", task["savepath"])
			relpath = os.path.relpath(task["savepath"])
			self.redirect("/" + relpath)
		else:
			self.custom_error("File Not Found", status_code = 404)

	def post(self, *args, **kwargs):
		method = "_post_%s" % args[0]
		if hasattr(self, method):
			getattr(self, method)()
		else:
			self.custom_error("参数错误")

	@tornado.web.asynchronous
	@gen.coroutine
	def _post_edit(self):
		profile = {}
		profile["email"] = self.get_body_argument("email", default=None)
		profile["website"] = self.get_body_argument("website", default=None)
		profile["qq"] = self.get_body_argument("qq", default=None)
		profile["address"] = self.get_body_argument("address", default=None)
		profile["signal"] = self.get_body_argument("signal", default=None)
		orgpass = self.get_body_argument("orgpass", default=None)
		if orgpass:
			password = self.get_body_argument("password")
			repassword = self.get_body_argument("repassword")
			if not password or len(password) < 5:
				self.custom_error("新密码太短")
			if password != repassword:
				self.custom_error("两次输入的密码不相同")
			user = yield self.db.member.find_one({"username": self.current_user["username"]})
			check = yield self.backend.submit(hash.verify, orgpass, user["password"])
			if not check:
				self.custom_error("原始密码输入错误")
			profile["password"] = yield self.backend.submit(hash.get, password)

		# check email
		ufemail = yield self.db.member.find_one({
			"email": profile["email"]
		})
		if ufemail:
			self.custom_error("邮箱已经被人使用过啦")

		# check user profile
		model = UserModel()
		if not model(profile):
			self.custom_error(model.error_msg)
		yield self.db.member.update({
			"username": self.current_user["username"]
		}, {
			"$set": profile
		})
		self.redirect("/user/edit")

	@tornado.web.asynchronous
	@gen.coroutine
	def _post_upface(self):
		img = self.get_body_argument("img", default = None)
		try:
			img = base64.b64decode(img)
			uid = self.current_user["_id"]
			face = "./static/face/%s/" % uid
			if not os.path.isdir(face):
				os.makedirs(face)
			face += "180.png"
			with open(face, "wb") as f:
				f.write(img)
			self.write("success")
		except:
			self.write("fail")

	@tornado.web.asynchronous
	@gen.coroutine
	def _post_message(self):
		openwebsite = intval(self.get_body_argument("openwebsite", default=1))
		openqq = intval(self.get_body_argument("openqq", default=1))
		openemail = intval(self.get_body_argument("openemail", default=1))
		allowemail = intval(self.get_body_argument("allowemail", default=1))
		yield self.db.member.find_and_modify({
			"username": self.current_user["username"]
		}, {
			"$set": {
				"openwebsite": openwebsite,
				"openqq": openqq,
				"openemail": openemail,
				"allowemail": allowemail
			}
		})
		self.redirect("/user/edit")

	@tornado.web.asynchronous
	@gen.coroutine
	def _post_like(self):
		id = self.get_body_argument("postid")
		yield self.db.article.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$pull": {"like": self.current_user["username"]}
		})
		self.redirect("/user/like")

	@tornado.web.asynchronous
	@gen.coroutine
	def _post_bookmark(self):
		id = self.get_body_argument("postid")
		yield self.db.member.find_and_modify({
			"username": self.current_user["username"]
		}, {
			"$pull": {"bookmark": {"id": id}}
		})
		self.redirect("/user/bookmark")

	@gen.coroutine
	def __get_sort(self, id):
		sort = yield self.db.sort.find_one({
			"_id": ObjectId(id)
		})
		raise gen.Return(sort)

	def radio(self, user, key, tr = 1):
		check = ""
		if key in user:
			if user[key] and tr == 1:
				check = "checked"
			if not user[key] and tr == 0:
				check = "checked"
		return '<input type="radio" name="%s" value="%d" %s>' % (key, tr, check)