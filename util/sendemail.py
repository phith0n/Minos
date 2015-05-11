# -*- coding: utf-8 -*-
__author__ = 'phithon'
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.escape import url_escape
from tornado import ioloop

def callback(self):
	pass

class Sendemail:
	def __init__(self, setting):
		AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
		self.url = setting.get("url")
		self.key = setting.get("key")
		self.sender = setting.get("sender")
		self.http_client = AsyncHTTPClient()

	def _parseurl(self, dic):
		ret = []
		for k, v in dic.items():
			ret.append("%s=%s" % (k, url_escape(v, False)))
		return "&".join(ret)

	def send(self, title, content, to, orgin = None, callback = callback):
		orgin = self.sender if not orgin else orgin
		url = "%s/messages" % self.url
		data = self._parseurl({
			"from": orgin,
			"to": to,
			"subject": title,
			"html": content
		})
		self.http_client.fetch(url, method = "POST", body = data, callback = callback, auth_username = "api", auth_password = self.key,
							follow_redirects = True, validate_cert = False)

if __name__ == "__main__":
	def main():
		setting = {
			"url": "https://api.mailgun.net/v3/domain",
			"key": "key-xxxxx"
		}
		Sendemail(setting).send(
			title = u"你好，test",
			content=u"这是一封测试邮件",
			to=u"test@qq.com",
			orgin=u"postmaster@domain"
		)

	io_loop = ioloop.IOLoop.instance()
	io_loop.run_sync(main)
	io_loop.start()
