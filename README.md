# Televic CoCon Client

> An asynchronous Python client for interacting with the Televic CoCon REST API.

This library provides a simple, type-safe interface for communicating with a Televic CoCon server. It supports long-polling for event notifications, command dispatching with automatic retries, and clean shutdown of background tasks.

---

## ✨ Features

- Async-friendly with `async with` support
- Long-polling notification handling
- Automatic command retries with exponential backoff
- Configurable behavior (timeouts, polling interval, retries)
- Typed and fully documented public API
- Minimal external dependencies

---

## 📦 Installation

Clone the repository and install it locally:

```bash
git clone https://your.git.repo.url/televic-CoCon-client.git
cd televic-CoCon-client
pip install .
```
> Requires **Python 3.11+**.

---

## 🚀 Quick Start

```python
import asyncio
from CoCon_client import CoConClient, Model

async def handle_notification(data: dict):
    print("Received:", data)

async def main():
    async with CoConClient("192.168.1.100", handler=handle_notification) as client:
        await client.subscribe([Model.DELEGATE, Model.MICROPHONE])
        await client.send("SomeCommand", {"param": "value"})
        await asyncio.sleep(10)

asyncio.run(main())
```

---

## ⚙️ Configuration

You can override default behavior using the `Config` dataclass:

```python
from CoCon_client import Config

custom_config = Config(
    poll_interval=2.0,
    max_retries=10,
    session_timeout=10.0
)

client = CoConClient("host", config=custom_config)
```
---

## 📄 License

This project is licensed under the **GNU AGPL v3 or later**. See [LICENSE](./LICENSE) for details.

---

## 🛠 Maintainers

Developed and maintained by **3P Technologies Srl**.
