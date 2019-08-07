import typing


class class2dictMeta(type):
	def __new__(cls, className: str, parents, attrs: typing.Dict[str, typing.Any], *args, **kwargs):
		newAttrs = type(attrs)(attrs)
		return {k: v for k, v in newAttrs.items() if k[0] != "_"}
