import typing
from collections import OrderedDict


class Record(OrderedDict):
	__slots__ = ("source", "ID")

	def __init__(self, *args, ID=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.source = None
		self.ID = ID

	__init__.__wraps__ = OrderedDict.__init__

	def get(self, ID: typing.Any) -> "Record":
		raise NotImplementedError()

	def __repr__(self):
		nRepr = super().__repr__()
		l = len(self.__class__.__name__) + 1
		return "".join((nRepr[:l], ("ID=" + repr(self.ID) + ", " if self.ID is not None else ""), nRepr[l:]))
