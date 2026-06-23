"""
services/exceptions.py
Custom exceptions for the service layer.
Routes catch these and convert them to appropriate HTTP responses.
"""


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class DuplicateError(Exception):
    """Raised when a uniqueness constraint would be violated (phone, national_id, etc.)."""


class UnauthorizedError(Exception):
    """Raised when request authentication is missing or invalid."""


class ForbiddenError(Exception):
    """Raised when an authenticated user lacks the required role."""


class ConflictError(Exception):
    """Raised when a requested relationship or account linkage conflicts."""


class InvalidTransitionError(Exception):
    """Raised when a status transition is not permitted by the business rules."""


class BusinessRuleError(Exception):
    """Generic guard for any other business rule violation."""
class ProcessingError(Exception):
    """Custom exception for errors during risk interpretation."""
