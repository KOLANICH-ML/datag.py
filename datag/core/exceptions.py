
class DataProcessingError(ValueError):
	pass

class DataParsingError(DataProcessingError):
	pass

class ValueParseFailed(DataParsingError):
	pass

class DataValidationError(DataProcessingError):
	pass

class InvalidUnitError(DataValidationError):
	pass

class InvalidRangeError(DataValidationError):
	pass

class GarbagePresentError(DataValidationError):
	pass
