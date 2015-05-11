#coding=utf-8
__author__ = 'phithon'
from model.base import BaseModel
try:
	type(u"a") is unicode
except:
	# PY3
	unicode = str

class UserModel(BaseModel):
	__table__ = "member"
	__invalid__ = {
		"username": {
			"_name": "用户名",
			"_need": True,
			"type": unicode,
			"max_length": 36,
			"min_length": 1,
			"pattern": ur"^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$"
		},
		"money": {
			"_name": "金币",
			"type": int,
			"min": 0
		},
		"email": {
			"_name": "Email",
			"type": unicode,
			"max_length": 64,
			"email": True
		},
		"website": {
			"_name": "个人主页",
			"type": unicode,
			"max_length": 128,
			"url": True
		},
		"address": {
			"_name": "地址",
			"type": unicode,
			"max_length": 256
		},
		"signal": {
			"_name": "签名",
			"type": unicode,
			"max_length": 512
		},
		"qq": {
			"_name": "QQ",
			"type": unicode,
			"max_length": 16,
			"min_length": 5,
			"number": True
		}
	}
	__msg__ = {
		"type": "%s类型错误",
		"max_length": "%s长度太长",
		"min_length": "%s长度太短",
		"max": "%s过大",
		"min": "%s过小",
		"email": "%s格式错误",
		"number": "%s必须是数字",
		"url": "%s格式错误",
		"pattern": "%s格式错误"
	}
	error_msg = ""