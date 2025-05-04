# Televic Cocon Client
An asynchronous Python client for interacting with the [Televic CoCon](https://televic-conference.com) system via its HTTP interface.
This client provides a high-level interface to manage subscriptions, send commands, and receive real-time notifications using long polling.
## Features
- Async client built with `aiohttp` and `asyncio`
- Handles `/Connect` and `/Notification` long polling automatically
- Queued command system with exponential backoff retries
- Supports subscribing/unsubscribing to specific CoCon models
- Customizable event handler for processing incoming data
- Graceful shutdown and automatic reconnection
- Optional logging integration
## Usage
