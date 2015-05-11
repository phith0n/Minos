#coding=utf-8
__author__ = 'phithon'
from model.base import BaseModel
try:
	type(u"a") is unicode
except:
	# PY3
	unicode = str

class SortModel(BaseModel):
	__table__ = "sort"
	__invalid__ = {
		"username": {
			"_name": "板块名称",
			"_need": True,
			"type": unicode,
			"max_length": 16,
			"min_length": 1
		},
		"intro": {
			"_name": "板块说明",
			"type": unicode,
			"max_length": 512
		}
	}
	__msg__ = {
		"type": "%s类型错误",
		"max_length": "%s长度太长",
		"min_length": "%s长度太短"
	}
	error_msg = ""