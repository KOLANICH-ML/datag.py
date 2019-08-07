from collections import OrderedDict
from .utils import class2dictMeta
from .Record import Record
import typing
import pint
from .actions import *
from .exceptions import *

PredicateFT = typing.Callable[[dict], bool]


class RuleBase:
	__slots__ = ("spec",)

	def __init__(self, condition: PredicateFT, fixer: FixerFT) -> None:
		raise NotImplementedError()

	def __call__(self, rec: Record, k: str) -> Record:
		raise NotImplementedError()


forgottenToReturnMessage = "You probably have forgotten to return the value from fixer "

class Rule(RuleBase):
	__slots__ = ("condition", "fixer", "triggered")

	def __init__(self, fixer: FixerFT, condition: PredicateFT):
		self.condition = condition
		self.fixer = fixer
		self.triggered = 0
		self.spec = None # set by 

	def __call__(self, rec: Record, k: str) -> Record:
		#print("self.condition is None", self.condition is None)
		#if self.condition is not None:
		#	print("self.condition(self, rec, k)", self.condition(self, rec, k))
		if self.condition is None or self.condition(self, rec, k):
			rec = self.fixer(self, rec, k)
			assert rec is not None, forgottenToReturnMessage + repr(self.fixer)
			self.triggered += 1
		return rec


class CompositeRule(RuleBase):
	__slots__ = ("rules",)

	def __init__(self, rules):
		self.rules = rules
		self.spec = None

	def __call__(self, rec: Record, k: str) -> Record:
		for r in self.rules:
			#print(r)
			rec = r(rec, k)
			assert rec is not None, forgottenToReturnMessage + repr(self.fixer)
		return rec


def defaultCondition(sself, rec, k):
	return True

class Spec(list):
	def __init__(self, specSeq, ureg=None):
		self.ureg = ureg
		super().__init__([None] * len(specSeq))
		for (i, (k, v)) in enumerate(specSeq):
			#print(i, k, v)
			if isinstance(v, tuple):
				if len(v) == 2:
					fixer, condition = v
					if not callable(condition):
						fixer = (fixer, condition)
						condition = None
				else:
					#raise ValueError("The tuple for "+repr(k)+" must have exactly 2 items")
					fixer = v
					condition = None
			else:
				fixer = v
				condition = None

			r = self.generateRule(k, fixer, condition)
			r.spec = self
			self[i] = (k, r)

	def generateRuleForTupleFixer(self, k, fixer, condition):
		if 2 <= len(fixer) <= 3:
			upstreamFixer, min = fixer[0:2]
		else:
			raise ValueError("fixer must be a tuple (unit, min, max) and condition must be None!")

		if len(fixer) == 3:
			max = fixer[2]
		else:
			max = float("inf")

		def rangeValidationFixer(selff, rec, k):
			raise InvalidRangeError("Value '" + k + "' (" + repr(rec[k]) + ") must be in range: [", min, max, "]")

		if condition is None:
			condition = defaultCondition

		def rangeValidationCondition(sself, rec, k):
			return condition(sself, rec, k) and not (min <= rec[k] <= max)

		return CompositeRule((self.generateRule(k, upstreamFixer, condition), self.generateRule(k, rangeValidationFixer, rangeValidationCondition)))

	def generateRule(self, k, fixer, condition):
		"""
		k arg is for debug output! Don't remove!
		"""
		#print(k, "generateRule isinstance(fixer="+repr(fixer)+", tuple)", isinstance(fixer, tuple))
		if isinstance(fixer, tuple):
			return self.generateRuleForTupleFixer(k, fixer, condition)

		#print(k, "generateRule condition is None", condition is None)
		if condition is None:
			condition = defaultCondition

		#print(k, "generateRule isinstance(fixer="+repr(fixer)+", self.ureg.Unit)", isinstance(fixer, self.ureg.Unit))
		if isinstance(fixer, self.ureg.Unit):
			unit = fixer

			def fixer(selff, rec, k):
				v = rec[k]
				if isinstance(v, pint.quantity._Quantity):
					try:
						rec[k] = v.to(unit).magnitude
					except pint.DimensionalityError:
						raise InvalidUnitError(repr(k) + ": " + repr(v) + " is of "+repr(v.units)+", which is inconvertible to " + repr(unit), v, unit)
				else:
					raise InvalidUnitError(repr(k) + ": " + repr(v) + " is dimensionless, but must be of " + repr(unit), v, unit)
				return rec

			return self.generateRule(k, fixer, condition)

		#print(k, "generateRule isinstance(fixer="+repr(fixer)+", type)", isinstance(fixer, type))
		if isinstance(fixer, type):
			tp = fixer

			def fixer(selff, rec, k):
				v = rec[k]
				if not isinstance(v, tp):
					raise InvalidUnitError(repr(k) + ": " + repr(v) + " must be of type " + repr(tp), k, v, tp)
				return rec

			return self.generateRule(k, fixer, condition)

		if isinstance(fixer, (set, frozenset)):
			st = frozenset(fixer)

			def fixer(selff, rec, k):
				v = rec[k]
				if v not in st:
					raise InvalidUnitError(repr(k) + ": " + repr(v) + " must be from set " + repr(st), k, v, st)
				return rec

			return self.generateRule(k, fixer, condition)

		if isinstance(fixer, typing._Final):
			from typeguard import check_type
			tp = fixer
			def fixer(selff, rec, k):
				v = rec[k]
				try:
					check_type(k, v, tp)
				except TypeError as e:
					raise InvalidUnitError(repr(k) + ": " + repr(v) + " : " + repr(e), k, v, tp)
				return rec
			return self.generateRule(k, fixer, condition)

		if callable(fixer):
			return Rule(fixer, condition)
		
		raise ValueError("Fixer " + repr(fixer) + " has inappropriate type")

	def __getitem__(self, k: typing.Union[str, int, None]):
		"""For debug purposes we can get rules by their names"""
		if isinstance(k, int):
			return super().__getitem__(k)
		else:
			res = []
			for kc, r in self:
				if kc == k:
					res.append(r)

			if len(res) == 1:
				return res[0]
			else:
				return res
