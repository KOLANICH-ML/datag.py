import typing
from .Source import Source
from .Spec import Spec
from .Record import Record


class Pipeline(Source):
	def __init__(self, spec: Spec, sources: typing.Iterable[Source]):
		self.spec = spec
		self.sources = sorted(sources, key=lambda s: s.priority)

	def getRaw(self, ID: typing.Any) -> Record:
		res = {}
		for s in self.sources:
			r.update(s.get(ID))
		return r
