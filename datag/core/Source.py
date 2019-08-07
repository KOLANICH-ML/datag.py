import typing
from .Record import Record
from .Spec import DataProcessingError, GarbagePresentError
import warnings
import pint
from pathlib import Path


class DiscardRecord(Exception):
	pass

def processWithSpec_(spec, rec, errorCallback=None):
	assert rec is not None
	for k, action in spec:
		if k is None or k in rec:
			try:
				rec = action(rec, k)
			except DataProcessingError as e:
				#print(errorCallback)
				if errorCallback is None:
					raise
				else:
					errorCallback(rec, k, e)
					continue
			except Exception as e:
				reprMsgAddition = repr(k)
				if rec.ID is not None:
					reprMsgAddition += ": (" + repr(rec.ID) + ")"
				
				if isinstance(e, pint.DimensionalityError):
					nex=e
					nex.extra_msg = reprMsgAddition + nex.extra_msg 
				else:
					if len(e.args) > 1:
						additionalArgs = e.args[1:]
					else:
						additionalArgs = []
					nex = type(e)(reprMsgAddition + ": " + e.args[0], *additionalArgs)
				nex.__cause__ = e
				nex.__suppress_context__ = False
				raise nex
	assert rec is not None
	return rec

def validate_(entity, rec, errorCallback=None):
	rec = processWithSpec_(entity.spec, rec=rec, errorCallback=errorCallback)
	assert rec
	
	garbage = {}
	for k in tuple(rec):
		if k not in entity.specKeys:
			garbage[k] = rec[k]
			del rec[k]
	
	if garbage:
		e = GarbagePresentError("The following properties that cannot be validated are present:", garbage)
		if errorCallback is None:
			raise e
		else:
			errorCallback(rec, None, e)
	return rec

class Source:
	priority = None
	entity = None

	def __init__(self):
		raise NotImplementedError()

	def getAllRaw(self) -> typing.Iterable[dict]:
		raise NotImplementedError()

	def getAll(self) -> typing.Iterable[typing.Mapping]:
		tmpRes = {}
		for rec in self.getAllRaw():
			try:
				rec = self.processRec(rec)
			except DiscardRecord:
				continue
			ID = rec.ID
			if ID not in tmpRes:
				tmpRes[ID] = ra = []
			else:
				ra = tmpRes[ID]
			#print(rec)
			ra.append(rec)

		return self.postProcess(tmpRes)
	
	def getTree(self) -> typing.Mapping[tuple, typing.Mapping]:
		return self.buildObjectTree(self.getAll())
	
	def buildObjectTree(self, aggRess):
		res = {}
		for aggRes in aggRess:
			parent = res
			for pathComp in aggRes.ID[:-1]:
				if pathComp not in res:
					res[pathComp] = parent = {}
				else:
					parent = res[pathComp]
			parent[aggRes.ID[-1]] = aggRes
		return res
	
	def postProcess(self, tmpRes):
		for ID, recs in tmpRes.items():
			aggRes = self.aggregate(recs)
			if aggRes:
				yield aggRes

	def processRec(self, rec: Record) -> Record:
		if not isinstance(rec, Record):
			rec = Record(rec)
		assert rec
		rec = self.transform(rec)
		assert rec
		rec = self.validate(rec)
		assert rec
		rec.ID = self.entity.getImmutableID(rec.ID)
		return rec

	def aggregate(self, recs: typing.Iterable[Record]):
		if len(recs) == 1:
			return recs[0]
		else:
			raise NotImplementedError("Multiple records with id", recs[0].ID)

	def getRaw(self, ID: typing.Any) -> dict:
		raise NotImplementedError()

	def get(self, ID: typing.Any) -> Record:
		rec = self.getRaw(ID)
		assert rec
		rec = self.processRec(rec)
		assert rec
		return rec

	def errorCallback(self, rec: Record, k, e):
		if isinstance(e, GarbagePresentError):
			warnings.warn(str(e))
		else:
			warnings.warn(repr(rec.ID) + " " + str(e))
			del rec[k]

	#errorCallback = None
	def selectSpec(self, rec):
		raise NotImplementedError()

	def transform(self, rec) -> Record:
		spec = self.selectSpec(rec)
		return processWithSpec_(spec, rec, errorCallback=self.errorCallback)

	def validate(self, rec) -> Record:
		if self.entity:
			return validate_(self.entity, rec, errorCallback=self.errorCallback)
		else:
			raise NotImplementedError("Implement the fucking `entity` property!")


class CachingSource(Source):
	cacheFilesPrefix = None
	
	def __init__(self, cacheDataFile: typing.Union[Path, str, "Cache.Cache"]=None):
		from Cache import Cache, compressors
		if cacheDataFile is None:
			cacheDataFile = Path("./"+self.__class__.cacheFilesPrefix+"Cache.sqlite")
		if not isinstance(cacheDataFile, Cache):
			cacheDataFile = Cache(cacheDataFile, compressors.none, commitOnNOps=50)
		self.cacheDataFile = cacheDataFile
	
	def get(self, ID: typing.Any) -> Record:
		if ID not in self.cacheDataFile:
			rec = super().get(ID)
			with self.cacheDataFile:
				self.cacheDataFile[rec.ID] = rec
				self.cacheDataFile.commit()
			return rec
		else:
			with self.cacheDataFile:
				return self.cacheDataFile[ID]
	
	def getAll(self) -> typing.Iterable[typing.Mapping]:
		res = super().getAll()
		with self.cacheDataFile:
			if not self.cacheDataFile:
				res = list(res)
				for el in res:
					self.cacheDataFile[el.ID] = el
		return res
	
