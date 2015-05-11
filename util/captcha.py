#!/usr/bin/python
# coding: utf-8

__author__ = 'outofmemory.cn'

from wheezy.captcha.image import captcha

from wheezy.captcha.image import background
from wheezy.captcha.image import curve
from wheezy.captcha.image import noise
from wheezy.captcha.image import smooth
from wheezy.captcha.image import text

from wheezy.captcha.image import offset
from wheezy.captcha.image import rotate
from wheezy.captcha.image import warp

import random
from os import path

_chars = 'ABCDEFGHJKMNPQRSTWXYZ23456789'

class Captcha:
	'''验证码'''
	_fontsDir = "./static/assets/fonts"
	_session_name_ = "captcha"

	@staticmethod
	def check(input, request):
		if input.upper() == request.session.get(Captcha._session_name_):
			request.session.delete(Captcha._session_name_)
			return True
		else:
			return False

	@staticmethod
	def get(request):
		captcha_image = captcha(drawings=[
			background(),
			text(fonts=[
				path.join(Captcha._fontsDir,'captcha.ttf')],
				drawings=[
					warp(),
					rotate(),
					offset()
				]),
			curve(),
			noise(),
			smooth()
		])
		chars = random.sample(_chars, 4)
		image = captcha_image(chars)
		request.session[Captcha._session_name_] = ''.join(chars)
		#print request.session[Captcha._session_name_]
		return image, ''.join(chars)
