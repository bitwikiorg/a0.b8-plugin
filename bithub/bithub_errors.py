"""Custom exception hierarchy for Bithub. 

This module defines the base exception class and specific error types
used throughout the Bithub library to replace dictionary-based error handling.
"""

class BithubError(Exception):
    """Base exception for all Bithub-related errors.

    This is the parent class for all custom exceptions in the Bithub library.
    Catching this exception will catch all Bithub-specific errors.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BithubAuthError(BithubError):
    """Raised when authentication fails or credentials are invalid.

    This exception is raised for issues such as:
    - Missing API keys
    - Invalid authentication tokens
    - Insufficient permissions (HTTP 401/403)
    """
    pass


class BithubNetworkError(BithubError):
    """Raised when a network operation fails.

    This exception covers low-level network issues such as:
    - Connection timeouts
    - DNS resolution failures
    - Unreachable hosts
    - Connection resets
    """
    pass


class BithubRateLimitError(BithubError):
    """Raised when the API rate limit is exceeded.

    This exception corresponds to HTTP 429 Too Many Requests responses.
    It indicates the client should back off before retrying.
    """
    pass
