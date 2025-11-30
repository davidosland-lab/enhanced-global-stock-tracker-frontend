"""
Notifications Package
=====================

Multi-channel notification system for stock screener alerts.

Supported channels:
- Telegram (text messages and file attachments)
"""

from .telegram_notifier import TelegramNotifier

__all__ = ['TelegramNotifier']
