class GoError(Exception):
    """Base error for Go engine."""

class OutOfBounds(GoError):
    pass

class OccupiedPoint(GoError):
    pass

class SuicideMove(GoError):
    pass

class KoViolation(GoError):
    pass
