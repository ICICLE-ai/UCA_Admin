# TODO: write custom logic inside exceptions
class RuleEngineError(Exception):
    pass

class RuleValidationError(RuleEngineError):
    pass

class RuleNotFoundError(RuleEngineError):
    pass