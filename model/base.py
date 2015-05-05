__author__ = 'phithon'
import re

class BaseModel:
	def __call__(self, *args, **kwargs):
		data = args[0]
		for (k, value) in data.items():
			if k not in self.__invalid__:
				continue
			if (not value) and ("_need" not in self.__invalid__[k]):
				continue
			for (field, limit) in self.__invalid__[k].items():
				if field[0] == "_": continue
				func = "_check_%s" % field
				if hasattr(self, func):
					ret = getattr(self, func)(limit, value)
					if not ret:
						self.error_msg = self.__msg__[field] % self.__invalid__[k]["_name"]
						return False
		return True

	def _check_type(self, valid, value):
		return type(value) is valid

	def _check_max_length(self, valid, value):
		return len(value) <= valid

	def _check_min_length(self, valid, value):
		return len(value) >= valid

	def _check_max(self, valid, value):
		return value <= valid

	def _check_min(self, valid, value):
		return value >= valid

	def _check_email(self, valid, value):
		return re.match(r"^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$", value)

	def _check_number(self, valid, value):
		return re.match(r"^\d+$", value)

	def _check_url(self, valid, value):
		return value.startswith("http://") or value.startswith("https://")

	def _check_pattern(self, valid, value):
		return re.match(valid, value)