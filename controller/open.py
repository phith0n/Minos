#coding=utf-8
__author__ = 'phithon'
import tornado.web, time, re, pymongo
from controller.base import BaseHandler
from tornado import gen
from bson.objectid import ObjectId
from util.captcha import Captcha
from util.function import intval, not_need_login, time_span

class PostHandler(BaseHandler):
	def initialize(self):
		BaseHandler.initialize(self)
		self.topbar = ""

	@not_need_login
	def prepare(self):
		BaseHandler.prepare(self)

	def del_with_hide(self, post):
		charge = post.get("charge")
		content = post.get('content')
		template = u"<div class=\"hidecont am-panel am-panel-default\">" \
				   u"<div class=\"am-panel-hd\">隐藏内容，需要登录并付费之后才能查看哦</div>" \
				   u"<div class=\"am-panel-bd\">需要" \
				   + str(post['charge']) + \
				   u"金币，点击 <a href=\"/login\">登录</a>" \
				   + u"</div></div>"
		pattern = re.compile(r"\[hide\](.*?)\[/hide\]", re.S)
		if charge == 0:
			post["content"] = pattern.sub("\\1", content)
			return post
		if pattern.search(content):
			content = pattern.sub(template, content)
		else:
			content = template
		post["content"] = content
		return post

	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		self.set_header("Content-Security-Policy", "default-src 'self'; script-src bdimg.share.baidu.com 'self' 'unsafe-eval'; "
												   "connect-src 'self'; img-src *.share.baidu.com nsclick.baidu.com 'self' data:; "
												   "style-src 'self' 'unsafe-inline'; font-src 'self'; frame-src 'self';")
		id = args[0]
		if self.current_user:
			self.redirect("/post/%s" % id)
		post = yield self.db.article.find_one({
			"_id": ObjectId(id),
			"open": True
		})
		if not post:
			self.custom_error("注册登录后才能查看哦", jump = "/register")

		post = self.del_with_hide(post)
		user = yield self.db.member.find_one({
			"username": post["user"]
		})
		yield self.db.article.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$inc": {"view": 1}
		})
		self.render("open_post.htm", post = post, user = user)

	@tornado.web.asynchronous
	@gen.coroutine
	def post(self, *args, **kwargs):
		captcha = self.get_body_argument("captcha")
		if not Captcha.check(captcha, self):
			self.custom_error("验证码错误")
		content = self.get_body_argument("content")
		postid = self.get_body_argument("postid")
		_id = ObjectId()
		post = yield self.db.article.find_and_modify({
				"_id": ObjectId(postid)
			},{
				"$push": {
					"comment": {
						"_id": _id,
						"content": content,
						"user": {
							"id": self.current_user["_id"],
							"username": self.current_user["username"]
						},
						"time": time.time()
					}
				}
			})
		if post:
			if self.current_user["username"] != post["user"]:
				self.message(fromuser=None, touser=post["user"],
					content=u"%s 评论了你的文章《%s》" % (self.current_user["username"], post["title"]),
					jump="/post/%s" % postid)
			self.at_user(content, post["title"], post["_id"], _id)
			self.redirect("/post/%s#%s" % (postid, _id))
		else:
			self.custom_error("不存在这篇文章")

	@gen.coroutine
	def at_user(self, content, title, postid, comid):
		at = []
		grp = re.findall(r"@([a-zA-Z0-9_\-\u4e00-\u9fa5]+)", content)
		for username in grp:
			try:
				user = yield self.db.member.find_one({
					"username": username
				})
				assert type(user) is dict
				assert self.current_user["username"] != username
				assert username not in at
				yield self.message(fromuser=None, touser=username,
					content=u"%s在文章《%s》中提到了你。" % (self.current_user["username"], title),
					jump="/post/%s#%s" % (postid, comid))
				at.append(username)
			except:
				continue

	@gen.coroutine
	def get_user(self, username):
		user = yield self.db.member.find_one({
			"username": {"$eq": username}
		})
		raise gen.Return(user)

class ListHandler(BaseHandler):
	@not_need_login
	def prepare(self):
		BaseHandler.prepare(self)

	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		limit = 15
		page = intval(args[1])
		if not page or page <= 0 : page = 1
		cursor = self.db.article.find({
			"open": True
		})
		cursor.sort([("top", pymongo.DESCENDING), ("lastcomment", pymongo.DESCENDING), ('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
		count = yield cursor.count()
		posts = yield cursor.to_list(length = limit)
		self.render("open_list.htm", posts = posts, page = page,
					time_span = time_span, count = count, each = limit)

	def test(self):
		pass