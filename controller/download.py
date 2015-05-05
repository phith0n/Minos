#coding=utf-8
__author__ = 'phithon'
import tornado.web, os
import tornado.gen

class DownloadHandler(tornado.web.StaticFileHandler):
	@tornado.gen.coroutine
	def get(self, path, include_body=True):
		filename = self.get_absolute_path(self.root, path)
		cookie = self.get_secure_cookie("download_key")
		if not cookie or cookie != filename:
			self.set_status(404)
			self.absolute_path = None
			self.render("404.htm")
			return
		yield super(DownloadHandler, self).get(path, include_body)

	def set_extra_headers(self, path):
		filename = os.path.basename(path)
		if "MSIE" in self.request.headers.get("User-Agent"):
			filename = filename.encode("gbk")
		self.set_header("Content-Type", "application/octet-stream")
		self.set_header("Content-Disposition", "attachment;filename=\"%s\";" % (filename, ))
		self.set_header("Content-Encoding", "none")
		self.set_header("Content-Transfer-Encoding", "binary")
		self.clear_header("Server")