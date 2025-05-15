# TELEVIC CoCon CLIENT
# __init__.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""
Top-level package for Televic CoCon client.
"""

# expose the client
from .client import CoConClient

# errors
from .errors import (
    CoConError,
    CoConConnectionError,
    CoConCommandError,
    CoConRetryError,
)

# types
from .types import AsyncHandler, ErrorHandler, CommandParams, Config, Model

__all__ = [
    "CoConClient",
    "Config",
    "Model",
    "CoConError",
    "CoConConnectionError",
    "CoConCommandError",
    "CoConRetryError",
    "AsyncHandler",
    "ErrorHandler",
    "CommandParams",
]
