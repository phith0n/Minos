#coding=utf-8
__author__ = 'phithon'
import tornado.web, time, os
from controller.base import BaseHandler
from tornado import gen
from util.function import humantime, md5, random_str, intval
from bson.objectid import ObjectId
from model.article import ArticleModel
from util.pxfilter import XssHtml

def xss_filter(html):
    parser = XssHtml()
    parser.feed(html)
    parser.close()
    return parser.getHtml()

class PublishHandler(BaseHandler):
    def initialize(self):
        super(PublishHandler, self).initialize()
        self.topbar = ""

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.set_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval' "
                                                    "'unsafe-inline'; connect-src 'self'; img-src 'self' data:; "
                                                    "style-src 'self' 'unsafe-inline'; font-src 'self' data:; frame-src 'self';")
        cursor = self.db.sort.find()
        sort = []
        while (yield cursor.fetch_next):
            sort.append(cursor.next_object())
        self.render("publish.htm", sort = sort, flash = self.flash)

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        content = self.get_body_argument("ckeditor", default=None)
        title = self.get_body_argument("title", default=None)
        sort = self.get_body_argument("sort", default=None)
        charge = intval(self.get_body_argument("charge", default=0))
        freebegin = intval(self.get_body_argument("freebegin", default=0))
        freeend = intval(self.get_body_argument("freeend", default=0))
        if not title:
            self.flash["article"] = content
            self.custom_error("标题不能为空哦", jump = "/publish")
        if charge < 0:
            self.flash["article"] = content
            self.custom_error("收费不能低于0", jump = "/publish")
        if freebegin > freeend:
            self.flash["article"] = content
            self.custom_error("结束时间不能小于开始时间", jump = "/publish")
        if not sort:
            self.flash["article"] = content
            self.custom_error("不存在这个分类", jump = "/publish")
        tosort = yield self.db.sort.find_and_modify({
            "_id": ObjectId(sort)
        }, {
            "$inc": {"article": 1}
        })
        if not tosort:
            self.flash["article"] = content
            self.custom_error("不存在这个分类", jump = "/publish")

        # filter html
        content = xss_filter(content)

        article = {
            "title": title,
            "content": content,
            "user": self.current_user["username"],
            "sort": tosort,
            "view": 0,
            "like": [],
            "unlike": [],
            "charge": charge,
            "time": time.time(),
            "freebegin": freebegin,
            "freeend": freeend,
            "buyer": [],
            "thanks": [],
            "star": False,
            "rank": 0,
            "comment": [],
            "open": False,
            "top": False,
            "lastcomment": time.time()
        }
        model = ArticleModel()
        if not model(article):
            self.flash["article"] = content
            self.custom_error(model.error_msg, jump = "/publish")
        id = yield self.db.article.insert(article)
        self.redirect("/post/%s" % id)


class EditHandler(BaseHandler):
    def initialize(self):
        super(EditHandler, self).initialize()
        self.topbar = ""

    def __check_power(self, post):
        if self.power == "admin":
            return True
        if not post or post["user"] != self.current_user["username"]:
            self.custom_error("你没有权限修改这篇文章", "", 0, "/post/%s" % post["_id"])
        if post["user"] == self.current_user["username"] and time.time() - post["time"] > 30 * 60:
            self.custom_error("文章发表30分钟后就不允许修改了", "", 0, "/post/%s" % post["_id"])

    def custom_error(self, info, content, id, jump = None):
        if not jump:
            self.flash["article"] = content
            return super(EditHandler, self).custom_error(info, jump = "/edit/%s" % id)
        else:
            return super(EditHandler, self).custom_error(info, jump = jump)

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.set_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval' "
                                                    "'unsafe-inline'; connect-src 'self'; img-src 'self' data:; "
                                                    "style-src 'self' 'unsafe-inline'; font-src 'self' data:; frame-src 'self';")
        id = args[0]
        post = yield self.db.article.find_one({
            "_id": ObjectId(id)
        })
        self.__check_power(post)
        cursor = self.db.sort.find()
        sort = []
        while (yield cursor.fetch_next):
            sort.append(cursor.next_object())
        self.render("edit.htm", sort = sort, post = post, flash = self.flash)

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        id = self.get_body_argument("id", default=None)
        if not id:
            self.custom_error("不存在这篇文章", "", id)
        post = yield self.db.article.find_one({
            "_id": ObjectId(id)
        })
        self.__check_power(post)
        content = self.get_body_argument("ckeditor", default=None)
        post["title"] = self.get_body_argument("title", default=None)
        sort = self.get_body_argument("sort", default=None)
        post["charge"] = intval(self.get_body_argument("charge", default=0))
        post["freebegin"] = intval(self.get_body_argument("freebegin", default=0))
        post["freeend"] = intval(self.get_body_argument("freeend", default=0))

        if not post["title"]:
            self.custom_error("标题不能为空", content, id)
        if post["charge"] < 0:
            self.custom_error("收费不能低于0", content, id)
        if post["freebegin"] > post["freeend"]:
            self.custom_error("结束时间不能小于开始时间", content, id)
        if not sort:
            self.custom_error("不存在这个分类", content, id)
        post["sort"] = yield self.db.sort.find_one({"_id": ObjectId(sort)})
        if not post["sort"]:
            self.custom_error("不存在这个分类", content, id)

        # filter html
        post["content"] = xss_filter(content)
        model = ArticleModel()
        if not model(post):
            self.custom_error(model.error_msg, content, id)
        yield self.db.article.find_and_modify({
            "_id": post["_id"]
        }, post)
        self.redirect("/post/%s" % id)

class UploadHandler(BaseHandler):
    def prepare(self):
        super(UploadHandler, self).prepare()
        self.orgname = ''

    def check_xsrf_cookie(self):
        return True

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        now = time.time()
        try:
            if self.request.files:
                file = self.request.files['upload'][0]
                ext = os.path.splitext(file["filename"])[-1]
                if ext not in (".png", ".gif", ".jpg", ".bmp", ".jpeg"):
                    self.end(False, u"不允许上传此类后缀的文件哦")
                self.orgname = file["filename"]
                filename = md5("%s%s" % (file["filename"], random_str(6))) + ext
                folder = "%s/%s/%s" % (self.settings["imagepath"], humantime(now, "%Y%m"),
                                            humantime(now, "%d"))
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                filename = "%s/%s" % (folder, filename)
                with open(filename, "wb") as fin:
                    fin.write(file["body"])
                self.end(True, u"上传成功", filename)
        except tornado.web.Finish, e:
            pass
        except:
            self.end(False, u"参数错误")

    def end(self, status, info, path = ""):
        self.write({
            "success": status,
            "msg": info,
            "file_path": path
        })
        raise tornado.web.Finish()