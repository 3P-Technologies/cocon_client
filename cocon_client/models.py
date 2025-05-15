# TELEVIC CoCon CLIENT
# models.py
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl

from enum import Enum


class Model(str, Enum):
    """Represents the various CoCon data models used in the API."""

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
