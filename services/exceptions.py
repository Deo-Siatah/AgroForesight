"""
services/exceptions.py
Custom exceptions for the service layer.
Routes catch these and convert them to appropriate HTTP responses.
"""


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class DuplicateError(Exception):
    """Raised when a uniqueness constraint would be violated (phone, national_id, etc.)."""


class InvalidTransitionError(Exception):
    """Raised when a status transition is not permitted by the business rules."""


class BusinessRuleError(Exception):
    """Generic guard for any other business rule violation."""
