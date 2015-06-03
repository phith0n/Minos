#coding=utf-8
__author__ = 'phithon'
import tornado.web, time, re
from controller.base import BaseHandler
from tornado import gen
from bson.objectid import ObjectId
from util.captcha import Captcha
from util.function import humantime

class PostHandler(BaseHandler):
	def initialize(self):
		BaseHandler.initialize(self)
		self.topbar = ""

	def is_edit(self, post):
		return post["user"] == self.current_user.get("username") and time.time() - post["time"] < 30 * 60

	def no_need_buy(self, post):
		if self.power == "admin":
			return True
		if post["user"] == self.current_user["username"]:
			return True
		if "buyer" in post and self.current_user["username"] in post["buyer"]:
			return True
		now = int(humantime(time.time(), "%H"))
		if post["freebegin"] <= now < post["freeend"]:
			return True
		return False

	def del_with_hide(self, post):
		charge = post.get("charge")
		content = post.get('content')
		template = u"<div class=\"hidecont am-panel am-panel-default\">" \
					u"<div class=\"am-panel-hd\">内容隐藏，付费以后才可以看哦</div>" \
					u"<div class=\"am-panel-bd\"><form method=\"post\" action=\"/buy\">需要" \
					+ str(post['charge']) + \
					u"金币，点击 <button type=\"submit\" class=\"am-btn am-btn-default am-btn-xs\">购买</button>" \
					+ self.xsrf_form_html() + u"<input name=\"id\" type=\"hidden\" " \
					u"value=\""+ str(post["_id"]) + u"\"></form></div></div>"
		pattern = re.compile(r"\[hide\](.*?)\[/hide\]", re.S)
		if charge == 0 or self.no_need_buy(post):
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
		post = yield self.db.article.find_one({
			"_id": ObjectId(id)
		})
		if not post:
			self.custom_error("你找的文章并不存在", jump = "/")

		post = self.del_with_hide(post)
		user = yield self.db.member.find_one({
			"username": post["user"]
		})
		yield self.db.article.find_and_modify({
			"_id": ObjectId(id)
		}, {
			"$inc": {"view": 1}
		})
		self.render("post.htm", post = post, user = user, is_edit = self.is_edit)

	@tornado.web.asynchronous
	@gen.coroutine
	def post(self, *args, **kwargs):
		captcha = self.get_body_argument("captcha", default=None)
		if self.settings["captcha"]["comment"] and not Captcha.check(captcha, self):
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
				},
				"$set": {
					"lastcomment": time.time()
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

class BuyHandler(BaseHandler):
	@tornado.web.asynchronous
	@gen.coroutine
	def post(self, *args, **kwargs):
		id = self.get_body_argument("id", default=None)
		if not id:
			self.custom_error("文章不存在")
		post = yield self.db.article.find_one({
			"_id": ObjectId(id)
		})
		if self.current_user["username"] in post["buyer"]:
			self.custom_error("已经购买过啦，无需重复购买", jump="/post/%s" % post["_id"])
		if post["charge"]:
			charge = int(post["charge"])
			old = yield self.db.member.find_and_modify({
				"username": {"$eq": self.current_user["username"]},
				"money": {"$gte": charge}
			}, {
				"$inc": {"money": 0 - charge}
			})
			if not old:
				self.custom_error("余额不够，不能购买帖子")
			post["buyer"].append(self.current_user["username"])
			yield self.db.article.find_and_modify({
				"_id": post["_id"]
			}, {
				"$set": {"buyer": post["buyer"]}
			})
			yield self.db.member.find_and_modify({
				"username": post["user"]
			}, {
				"$inc": {"money": charge}
			})
			self.clear_cookie("flush_info")
			self.redirect("/post/%s" % post["_id"])
		else:
			self.custom_error("这篇文章并不需要付费", jump="/post/%s" % post["_id"])