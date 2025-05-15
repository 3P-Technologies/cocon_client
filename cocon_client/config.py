# TELEVIC CoCon CLIENT
# config.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl


from dataclasses import dataclass


@dataclass(slots=True)
class Config:
    """Configuration for CoConClient behavior."""

    poll_interval: float = 1.0
    max_retries: int = 5
    backoff_base: float = 0.5
    session_timeout: float = 7.0
