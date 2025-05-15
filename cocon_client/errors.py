# TELEVIC CoCon CLIENT
# errors.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl


class CoConError(Exception):
    """Base class for all client errors."""

    pass


class CoConConnectionError(CoConError):
    """
    Raised when the client fails to establish a connection with the CoCon server.

    This may happen if the server is offline, unreachable, or responds with a failure during the
    initial connection handshake.
    """

    pass


class CoConCommandError(CoConError):
    """Raised when a command sent to the API fails."""

    def __init__(self, endpoint: str, status: int, body: str | None = None) -> None:
        """Initialize the command error with endpoint, status code, and optional response body.

        Args:
            endpoint (str): The API endpoint that failed.
            status (int): HTTP status code returned.
            body (str | None, optional): Optional response body for error inspection.
                Defaults to None.
        """
        super().__init__(f"'/{endpoint}' failed with HTTP {status}")
        self.endpoint: str = endpoint
        self.status: int = status
        self.body: str | None = body


class CoConRetryError(CoConError):
    """
    Raised when a retryable operation exceeds the maximum number of retry attempts.

    Commonly occurs when repeated transient failures (e.g. timeouts) persist beyond the configured
    limit in `Config.max_retries`.
    """

    pass
