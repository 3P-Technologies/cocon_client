# TELEVIC CoCon CLIENT
# __init__.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
"""
Top-level package for Televic CoCon client.
"""

# expose the client
from .client import CoConClient

# config
from .config import Config

# models
from .models import Model

# errors
from .errors import (
    CoConError,
    CoConConnectionError,
    CoConCommandError,
    CoConRetryError,
)

# types
from .types import AsyncHandler, ErrorHandler, CommandParams

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
