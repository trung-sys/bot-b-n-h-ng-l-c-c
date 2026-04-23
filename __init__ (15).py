from __future__ import annotations


class AppError(Exception):
    """Base application error."""


class ValidationError(AppError):
    """Raised when user or config input is invalid."""


class BusinessRuleError(AppError):
    """Raised for expected domain rule violations."""


class DuplicateOperationError(BusinessRuleError):
    """Raised when an idempotent action was already processed."""

