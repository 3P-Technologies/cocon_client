# TELEVIC COCOON CLIENT
# client.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl

import asyncio
import aiohttp
import random
import inspect
import logging
from asyncio import Task
from aiohttp import ClientSession, ClientTimeout, ClientResponseError
from typing import Callable, TypeVar, Awaitable, Any, Self
from types import TracebackType
from enum import Enum
from dataclasses import dataclass

T = TypeVar("T")

logger = logging.getLogger(__name__)

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="[{levelname}] {asctime} - {name} {message}",
        style="{",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


class Model(str, Enum):
    """Represents the various CoCoon data models used in the API."""

    ROOM = "Room"
    MICROPHONE = "Microphone"
    MEETING_AGENDA = "MeetingAgenda"
    VOTING = "Voting"
    TIMER = "Timer"
    DELEGATE = "Delegate"
    AUDIO = "Audio"
    INTERPRETATION = "Interpretation"
    LOGGING = "Logging"
    BUTTON_LED_EVENT = "ButtonLED_Event"
    INTERACTIVE = "Interactive"
    EXTERNAL = "External"
    INTERCOM = "Intercom"
    VIDEO = "Video"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


class _EP(str, Enum):
    """Internal enumeration of known API endpoints."""

    CONNECT = "Connect"
    NOTIFICATION = "Notification"


class CoCoonError(Exception):
    """Base class for all client errors."""


class CoCoonConnectionError(CoCoonError):
    """Raised when a connection attempt fails."""

    pass


class CoCoonCommandError(CoCoonError):
    """Raised when a command sent to the API fails."""

    def __init__(self, endpoint: str, status: int, body: str | None = None) -> None:
        """Initialize the command error with endpoint, status code, and optional response body.

        Args:
            endpoint (str): The API endpoint that failed.
            status (int): HTTP status code returned.
            body (str | None, optional): Optional response body for error inspection. Defaults to None.
        """
        super().__init__(f"'/{endpoint}' failed with HTTP {status}")
        self.endpoint: str = endpoint
        self.status: int = status
        self.body: str | None = body


class CoCoonRetryError(CoCoonError):
    """Raised when a retryable operation exceeds max retries."""

    pass


@dataclass(slots=True)
class Config:
    """Configuration for CoCoonClient behavior."""

    poll_interval: float = 1.0
    max_retries: int = 5
    backoff_base: float = 0.5
    session_timeout: float = 7.0


class CoCoonClient:
    """
    Asynchronous client for interacting with the Televic Cocoon REST interface.

    Supports long-polling notifications, command sending, and model subscriptions.
    """

    def __init__(
        self,
        url: str,
        port: int = 8890,
        handler: Callable[[dict], Awaitable[None]] | None = None,
        on_handler_error: Callable[[Exception, dict], None] | None = None,
        config: Config | None = None,
    ) -> None:
        """
        Initialize the CoCoonClient with connection settings and optional event handlers.

        Args:
            url (str): The hostname or IP address of the CoCon server.
            port (int): The port to connect to on the server. Defaults to 8890.
            handler (Callable[[dict], Awaitable[None]] | None): An async function to handle incoming notification data. Defaults to None
            on_handler_error (Callable[[Exception, dict], None] | None): A callback invoked when the handler raises an exception. Defaults to None
            config (Config): Optional Config object to override default timing and retry settings.
        """
        self.base_url: str = f"http://{url}:{port}/CoCoon"
        self._connect_url: str = f"{self.base_url}/{_EP.CONNECT}"
        self._notify_url: str = f"{self.base_url}/{_EP.NOTIFICATION}"
        self._shutdown_event = asyncio.Event()
        self.session: ClientSession | None = None
        self._command_queue: asyncio.Queue[tuple[str, dict[str, str]]] = asyncio.Queue(
            maxsize=1000
        )
        self._subscriptions: set[str] = set()
        self._handler: Callable[[dict], Awaitable[None]] | None = handler
        self._on_handler_error = on_handler_error
        self.config: Config = config or Config()
        self._connection_id: str = ""

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Initializes the aiohttp session and starts the supervisor task which manages polling and command processing.

        Returns:
            Self: The initialized CoCoonClient instance.
        """
        self.session = aiohttp.ClientSession(
            timeout=ClientTimeout(self.config.session_timeout)
        )

        self._supervisor_task: Task = asyncio.create_task(
            self._supervise(), name="supervisor"
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        Signals shutdown, cancels or completes the supervisor task, calls the close method to clean up the queue, and closes the HTTP session.

        Args:
            exc_type (type[BaseException] | None): Exception type if raised during the context.
            exc (BaseException | None): Exception instance.
            tb (TracebackType | None): Traceback object.

        Raises:
            Exception: If session is None raise.
        """
        if self.session is None:
            raise Exception("Session is None.")

        self._shutdown_event.set()
        if exc_type:
            self._supervisor_task.cancel()
            await asyncio.gather(self._supervisor_task, return_exceptions=True)
        else:
            await self._supervisor_task
        await self.close()
        await self.session.close()

    async def _supervise(self) -> None:
        """Supervises polling and command loop tasks, handling errors and task cancellation.


        Raises:
            Any exception raised by the polling or command loop.
        """
        poll_task: Task = asyncio.create_task(self._poll_loop(), name="poll_loop")
        command_task: Task = asyncio.create_task(
            self._command_loop(), name="command_loop"
        )

        done, pending = await asyncio.wait(
            {poll_task, command_task}, return_when=asyncio.FIRST_EXCEPTION
        )

        first_exc: BaseException | None = None
        for t in done:
            first_exc = t.exception()
            if first_exc:
                logger.error("supervisor-task %s failed: %s", t.get_name(), first_exc)

        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        if first_exc is not None:
            raise first_exc

    async def _poll_loop(self) -> None:
        """Handles long polling with automatic reconnection on failure."""
        while not self._shutdown_event.is_set():
            try:
                await self._connect_and_poll()
            except Exception as exc:
                logger.error("polling-loop fatal: %s", exc)
                await asyncio.sleep(1)  # avoid tight loop on fatal error

    async def _connect(self) -> str:
        """Request a new connection ID from the CoCoon API.

        Raises:
            Exception: If the session is None, or if the call return 200 but the connect field in the response is set to False, or if the connection ID is missing from the response.
            CoCoonConnectionError: If the connection failed.

        Returns:
            str: A valid connection ID.
        """
        if self.session is None:
            raise Exception("Session is None.")

        async with self.session.post(self._connect_url) as resp:
            if resp.status != 200:
                raise CoCoonConnectionError(
                    f"'/{_EP.CONNECT}' failed with status {resp.status}"
                )

            json = await resp.json()
            if not json.get("Connect"):
                raise Exception(
                    f"'/{_EP.CONNECT}' call returned 200 but connect in response is False"
                )

            conn_id: str = json.get("id")
            if not conn_id:
                raise Exception(f"'/{_EP.CONNECT}' missing connection id in response")
            logger.info("/%s OK - connection established", _EP.CONNECT)
            logger.debug("/%s OK - connection id=%s", _EP.CONNECT, conn_id)
            return conn_id

    async def _notify(self) -> None:
        """Perform the notify long-poll request and dispatch data to the handler.

        Raises:
            Exception: If session is None.
            ClientResponseError: If HTTP response is not
        """
        if self.session is None:
            raise Exception("Session is None.")

        url = f"{self._notify_url}?id={self._connection_id}"
        async with self.session.get(url, timeout=ClientTimeout(total=35.0)) as resp:
            if resp.status != 200:
                raise ClientResponseError(resp.request_info, (), status=resp.status)
            data = await resp.json()
            await self._handle_incoming(data)

    async def _resubscribe(self) -> None:
        """Resend subscriptions after reconnecting."""
        for model in self._subscriptions:
            await self._send_command(
                "Subscribe",
                {"Model": model, "id": self._connection_id, "details": "true"},
            )

    async def _connect_and_poll(self) -> None:
        """Handles full connect-then-notify cycle including auto-reconnect on 400 and 408 errors."""
        self._connection_id = await self._retry_with_backoff(self._connect)

        while not self._shutdown_event.is_set():
            try:
                await self._notify()
            except ClientResponseError as exc:
                match exc.status:
                    case 400:
                        logger.warning(
                            "/%s 400 - invalid connection id, reconnecting",
                            _EP.NOTIFICATION,
                        )
                        logger.debug(
                            "/%s 400 - connection id used=%s",
                            _EP.NOTIFICATION,
                            self._connection_id,
                        )
                        self._connection_id = await self._retry_with_backoff(
                            self._connect
                        )
                        await self._resubscribe()
                    case 408:
                        logger.warning(
                            "/%s 408 - channel timed out, retrying notify",
                            _EP.NOTIFICATION,
                        )
                    case _:
                        logger.error(
                            "/%s %d- unexpected error: %s, retrying",
                            _EP.NOTIFICATION,
                            exc.status,
                            exc,
                        )
                        await asyncio.sleep(1)

    async def _send_command(self, endpoint: str, params: dict[str, str]) -> Any:
        if self.session is None:
            raise Exception("Session is None.")

        url = f"{self.base_url}/{endpoint}"

        async def _send() -> Any | str:
            if self.session is None:
                raise Exception("Session is None.")
            async with self.session.post(url, params=params) as resp:
                if resp.status != 200:
                    body: str = await resp.text()
                    raise CoCoonCommandError(endpoint, resp.status, body)
                logger.info("/%s - sent successfully", endpoint)

                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await resp.json()
                else:
                    return await resp.text()

        return await self._retry_with_backoff(_send)

    async def _command_loop(self) -> None:
        while not self._shutdown_event.is_set():
            try:
                endpoint, params = await asyncio.wait_for(
                    self._command_queue.get(), timeout=self.config.poll_interval
                )
                try:
                    await self._send_command(endpoint, params)
                finally:
                    self._command_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.error("error sending command: %s", exc)

    async def _retry_with_backoff(self, task_func: Callable[[], Awaitable[T]]) -> T:
        attempt = 0
        while self.config.max_retries < 0 or attempt < self.config.max_retries:
            try:
                return await task_func()
            except Exception as exc:
                delay = min(
                    self.config.backoff_base * 2**attempt + random.uniform(0, 1), 30
                )
                logger.warning("retry %s after %.2fs - %s", attempt + 1, delay, exc)
                await asyncio.sleep(delay)
                attempt += 1
        raise CoCoonRetryError("Max retries exceeded.")

    async def _handle_incoming(self, data: dict) -> None:
        if self._handler:
            try:
                if inspect.iscoroutinefunction(self._handler):
                    await self._handler(data)
                else:
                    await asyncio.to_thread(self._handler, data)
            except Exception as exc:
                logger.error("handler raised %s (data=%s)", exc, data, exc_info=True)
                if self._on_handler_error is not None:
                    try:
                        self._on_handler_error(exc, data)
                    except Exception as hook_exc:
                        logger.error("on_handler_error failed - %s", hook_exc)
        else:
            logger.info("received: %s", data)

    async def open(self):
        async with aiohttp.ClientSession(
            timeout=ClientTimeout(self.config.session_timeout)
        ) as session:
            self.session = session
            await self._supervise()

    async def close(self):
        self._shutdown_event.set()

        if hasattr(self, "_supervisor_task"):
            self._supervisor_task.cancel()
            await asyncio.gather(self._supervisor_task, return_exceptions=True)

        while not self._command_queue.empty():
            try:
                self._command_queue.get_nowait()
                self._command_queue.task_done()
            except asyncio.QueueEmpty:
                break

        await self._command_queue.join()

    async def send(self, endpoint: str, params: dict[str, str]):
        await self._command_queue.put((endpoint, params))

    async def subscribe(self, models: list[str | Model], details: bool | str = True):
        for model in models:
            await self._send_command(
                "Subscribe",
                {
                    "Model": str(model),
                    "id": self._connection_id,
                    "details": str(details).lower(),
                },
            )
            self._subscriptions.add(str(model))

    async def unsubscribe(self, models: list[str | Model]):
        for model in models:
            await self._send_command(
                "Unsubscribe",
                {
                    "Model": str(model),
                    "id": self._connection_id,
                },
            )
            self._subscriptions.discard(str(model))

    async def set_handler(self, handler: Callable[[dict], Awaitable[None]]):
        self._handler = handler
