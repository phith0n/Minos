#!/usr/bin/python
import tornado.ioloop
import tornado.web, tornado.options
import motor, sys, os, yaml
from concurrent import futures
import controller.base

tornado.options.define("port", default=8765, help="Run server on a specific port", type=int)
tornado.options.define("host", default="localhost", help="Run server on a specific host")
tornado.options.define("url", default=None, help="Url to show in HTML")
tornado.options.parse_command_line()

if not tornado.options.options.url:
	tornado.options.options.url = "http://%s:%d" % (tornado.options.options.host, tornado.options.options.port)

setting = {
	"base_url": tornado.options.options.url,
	"template_path": "templates",
	"cookie_secret": "s3cr3tk3y",
	"config_filename": "config.yaml",
	"compress_response": True,
	"default_handler_class": controller.base.NotFoundHandler,
	"xsrf_cookies": True,
	"static_path": "static",
	"download": "./download",
	"session": {
		"driver": "redis",
		"driver_settings": {
			"host": "localhost",
			"port": 6379,
			"db": 1
		},
		"force_persistence": False,
		"cache_driver": True,
		"cookie_config": {
			"httponly": True
		},
	},
	"thread_pool": futures.ThreadPoolExecutor(4)
}

# config file
config = {}
try:
	with open(setting["config_filename"], "r") as fin:
		config = yaml.load(fin)
	for k, v in config["global"].items():
		setting[k] = v
	if "session" in config:
		setting["session"]["driver_settings"] = config["session"]
except:
	print "cannot found config.yaml file"
	sys.exit(0)

# mongodb connection
# format: mongodb://user:pass@host:port/
# database name: minos

try:
	client = motor.MotorClient(config["database"]["config"])
	database = client[config["database"]["db"]]
	setting["database"] = database
except:
	print "cannot connect mongodb, check the config.yaml"
	sys.exit(0)

application = tornado.web.Application([
	(r"^/public/post/([a-f0-9]{24})", "controller.open.PostHandler"),
	(r"^/public/list(/(\d*))?", "controller.open.ListHandler"),
	(r"^/(page/(\d+))?", "controller.main.HomeHandler"),
	(r"^/login", "controller.auth.LoginHandler"),
	(r"^/register", "controller.auth.RegisterHandler"),
	(r"^/nologin/([a-z]+)", "controller.auth.AjaxHandler"),
	(r"^/forgetpwd", "controller.auth.ForgetpwdHandler"),
	(r"^/captcha\.png", "controller.auth.CaptchaHanlder"),
	(r"^/user/([a-z]+)(/(.*))?", "controller.user.UserHandler"),
	(r"^/admin/([a-z]+)?", "controller.admin.AdminHandler"),
	(r"^/publish", "controller.publish.PublishHandler"),
	(r"^/edit/([a-f0-9]{24})", "controller.publish.EditHandler"),
	(r"^/uploader", "controller.publish.UploadHandler"),
	(r"^/post/([a-f0-9]{24})", "controller.post.PostHandler"),
	(r"^/ajax/([a-z]+)", "controller.ajax.AjaxHandler"),
	(r"^/sort/([a-f0-9]{24})(/(\d+))?", "controller.sort.SortHandler"),
	(r"^/search(/(\d+))?", "controller.search.SearchHandler"),
	(r"^/buy", "controller.post.BuyHandler"),
	(r"^/message(/(\d+))?", "controller.message.MessageHandler"),
	(r"^/message/([a-f0-9]{24})", "controller.message.DetailHandler"),
	(r"^/manage/([a-z]+)(/(.*))?", "controller.dashboard.AdminHandler"),
	(r"^/download/(.*)", "controller.download.DownloadHandler", {"path": "./download/"})
], **setting)

if __name__ == "__main__":
	try:
		application.listen(tornado.options.options.port)
		tornado.ioloop.IOLoop.instance().start()
	except:
		import traceback
		print traceback.print_exc()
	finally:
		sys.exit(0)