import typing
from .Record import Record
import re
import unicodedata
from .exceptions import DataParsingError, ValueParseFailed

FixerFT = typing.Callable[[dict], None]

class Action:
	__slots__ = ()

	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		raise NotImplementedError()


class CallableAdapter(Action):
	__slots__ = ("f",)

	def __init__(self, f: typing.Callable):
		super().__init__()
		self.f = f


class SingleValueAction(Action):
	__slots__ = ()

	def singleValue(self, v: typing.Any) -> typing.Any:
		raise NotImplementedError()

	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		rec[k] = self.singleValue(rec[k])
		return rec


class ActionAdapter(Action):
	__slots__ = ("a",)

	def __init__(self, *a: typing.Iterable[FixerFT]):
		super().__init__()
		self.a = a

	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		for a in self.a:
			rec = a(sself, rec, k)
		return rec


class Apply(CallableAdapter, SingleValueAction):
	__slots__ = ()

	def singleValue(self, v):
		return self.f(v)

class ReplaceStr(SingleValueAction):
	__slots__ = ("template", "replacement")

	def __init__(self, template:str, replacement:str):
		super().__init__()
		self.template = template
		self.replacement = replacement

	def singleValue(self, v:str):
		return v.replace(self.template, self.replacement)

class ReplaceRX(SingleValueAction):
	__slots__ = ("template", "replacement")

	def __init__(self, template:"re.Pattern", replacement:typing.Union[str, typing.Callable]):
		super().__init__()
		self.template = template
		self.replacement = replacement

	def singleValue(self, v):
		return self.template.subn(self.replacement, v)

class Update(CallableAdapter):
	__slots__ = ()

	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		rec.update(self.f(rec[k]))
		return rec


class Version(SingleValueAction):

	__slots__ = ("groups", "delimiter")

	def __init__(self, groups:int=1, delimiter:str="."):
		super().__init__()
		self.groups = groups
		self.delimiter = delimiter

	def singleValue(self, v: str):
		groups = v.split(self.delimiter)
		if len(groups) > self.groups:
			raise ValueError("Seems to be an invalid version. Contains " + repr(len(v)) + " groups instead of " + repr(self.groups)+ ": " + v)
		for i in range(len(groups)):
			try:
				groups[i] = int(groups[i])
			except ValueError:
				raise ValueError("Seems to be an invalid version. Group " + repr(i) + " is not a decimal int: " + repr(v[i]))
		groups += [0]*(self.groups - len(groups))
		res = tuple(groups)
		if self.groups == 1:
			res = res[0]
		return res


class ApplyUnit(SingleValueAction):

	__slots__ = ("unit",)

	def __init__(self, unit: typing.Callable):
		super().__init__()
		self.unit = unit

	def singleValue(self, v: str):
		if isinstance(v, (int, float)):
			return self.unit._REGISTRY.Quantity(v, self.unit)
		raise ValueError("Value must be either an int or a float, but has type " + repr(type(v)))

def precleanStr(v:str) -> str:
	return "".join(c for c in unicodedata.normalize("NFKD", v) if c.isprintable()).strip()

class Parse(Action):
	"""Subclass it if you need other values"""

	__slots__ = ()
	missingDataPlaceholders = frozenset(("N/A", "n/a"))
	exactRemap = {
		"yes": True,
		"no": False,
		"true": True,
		"false": False
	}
	stopWords = ()
	numberRx = "\\d+(?:[\\.,]\\d+)?"
	carveRX = re.compile(numberRx + "\\s*(?:[\\w*/'\"°]+)?")  # fill a PR if I missed something

	def carveFirstQuantity(self, v):
		try:
			return self.carveRX.search(v).group(0)
		except BaseException:
			return v
	
	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		v = rec[k]
		v = precleanStr(v)
		if not len(v) or v in self.missingDataPlaceholders or self.checkStopWords(v):
			raise ValueParseFailed("Empty value")
		elif v in self.exactRemap:
			v = self.exactRemap[v]
		else:
			try:
				res = []
				v = self.carveFirstQuantity(v)
				v = sself.spec.ureg.parse_expression(v)
				v = v.to_base_units() if not isinstance(v, (int, float)) else v
			except Exception as ex:
				raise ValueParseFailed("", ex)
		rec[k] = v
		return rec

	def checkStopWords(self, msg: str) -> bool:
		for w in self.stopWords:
			if w in msg:
				return True
		return False

class Drop(ActionAdapter):
	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		rec = super().__call__(sself, rec, k)
		if k in rec:
			del rec[k]
		return rec


class Rename(ActionAdapter):
	__slots__ = ("newName",)

	def __init__(self, newName: str, *a: typing.Iterable[FixerFT]):
		super().__init__(*a)
		self.newName = newName

	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		rec = super().__call__(sself, rec, k)
		if k in rec:
			if self.newName in rec:
				raise KeyError("Fuck, " + self.newName + " is already there, unable to rename!")
			rec[self.newName] = rec[k]
			del rec[k]
		return rec


class ID(ActionAdapter):
	"""
	Moves the field to identifiers.
	Contained actions MUST NOT CONTAIN RENAMINGS OR DELETIONS OF THE ATTRS OF THAT KEY!
	"""

	__slots__ = ()

	def __init__(self, *a: typing.Iterable[FixerFT]):
		super().__init__(*a)

	def __call__(self, sself: "RuleBase", rec: "Record", k: str):
		rec = super().__call__(sself, rec, k)
		if not isinstance(rec, Record):
			rec = Record(rec)

		if rec.ID is None:
			rec.ID = {}
		rec.ID[k] = rec[k]
		del rec[k]
		return rec
