# TELEVIC CoCon CLIENT
# types.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl


from typing import TypeVar, NamedTuple, Callable, Awaitable, Any
from asyncio import Future

T = TypeVar("T")
JSON = dict[str, Any]
CommandParams = dict[str, str] | None

# Signature for your user-supplied notification handler
AsyncHandler = Callable[[JSON], Awaitable[None]]

# Signature for the on_handler_error callback
ErrorHandler = Callable[[Exception, JSON], None]


class QueuedCommand(NamedTuple):
    """
    Internal command queue payload.

    Attributes:
        endpoint: The CoCon API endpoint name (e.g. "Subscribe").
        params:  Optional query parameters.
        future:  asyncio.Future that will be set with the response.
    """

    endpoint: str
    params: CommandParams | None
    future: Future[Any]
