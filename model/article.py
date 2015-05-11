#coding=utf-8
__author__ = 'phithon'
from model.base import BaseModel

class ArticleModel(BaseModel):
	__table__ = "article"
	__invalid__ = {
		"title": {
			"_name": "标题",
			"type": unicode,
			"max_length": 200,
			"min_length": 1
		},
		"charge": {
			"_name": "金币数值",
			"type": int,
			"min": 0,
			"max": 100
		},
		"freebegin": {
			"_name": "开始时间",
			"type": int,
			"min": 0,
			"max": 24
		},
		"freeend": {
			"_name": "结束时间",
			"type": int,
			"min": 0,
			"max": 24
		}
	}
	__msg__ = {
		"type": "%s类型错误",
		"max_length": "%s长度太长",
		"min_length": "%s长度太短",
		"max": "%s过大",
		"min": "%s过小"
	}
	error_msg = ""