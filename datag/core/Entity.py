from .Spec import Spec, Rule
from .actions import ID
NoneType = type(None)

class Entity:
	__slots__ = ("spec", "specKeys", "idSeq")

	def __init__(self, spec: Spec):
		self.spec = spec
		idSeq = []
		specKeys = []
		for k, rule in spec:
			specKeys.append(k)
			if isinstance(rule, Rule) and isinstance(rule.fixer, ID):
				idSeq.append(k)

		if not idSeq:
			raise ValueError("Spec must define the way based on which we identify and merge records")
		self.idSeq = tuple(idSeq)
		self.specKeys = set(specKeys)

	@property
	def ureg(self):
		return self.spec.ureg

	def getImmutableID(self, mutableId: dict) -> tuple:
		if not isinstance(mutableId, (tuple, NoneType)):
			mutableIdCopy = type(mutableId)(mutableId)
			res = [None] * len(self.idSeq)
			for i, k in enumerate(tuple(self.idSeq)):
				if k in mutableIdCopy:
					res[i] = mutableIdCopy[k]
					del mutableIdCopy[k]
				else:
					res[i] = None
			res = tuple(res)
			if mutableIdCopy:
				raise ValueError("Some parts of ID for " + repr(res) + " are not a part of a spec: " + repr(mutableIdCopy))
			return res
		return mutableId
