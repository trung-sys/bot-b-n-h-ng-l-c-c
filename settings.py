from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import Future
from typing import Any

from telegram.ext import Application


class TelegramBotController:
    def __init__(self, settings, handlers, logger: logging.Logger) -> None:
        self.settings = settings
        self.handlers = handlers
        self.logger = logger
        self._application: Application | None = None
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event = threading.Event()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="telegram-bot", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=15)
        self._thread = None

    def _build_application(self) -> Application:
        application = Application.builder().token(self.settings.bot_token).build()
        self.handlers.register(application)
        return application

    def _run(self) -> None:
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            self._loop = asyncio.get_event_loop()
            self._application = self._build_application()

            async def runner() -> None:
                assert self._application is not None
                await self._application.initialize()
                await self._application.start()
                try:
                    me = await self._application.bot.get_me()
                    self.handlers.set_bot_username(me.username or "")
                    self.logger.info("Telegram bot username: @%s", me.username)
                except Exception:
                    self.logger.exception("Failed to fetch bot username.")
                await self._application.updater.start_polling(drop_pending_updates=True)
                while not self._stop_event.is_set():
                    await asyncio.sleep(0.5)
                await self._application.updater.stop()
                await self._application.stop()
                await self._application.shutdown()

            self.logger.info("Telegram bot starting.")
            self._loop.run_until_complete(runner())
            self.logger.info("Telegram bot stopped.")
        except Exception:
            self.logger.exception("Telegram bot thread crashed.")

    def send_message(self, chat_id: int, text: str, **kwargs: Any) -> Future | None:
        if not self._application or not self._loop or not self.is_running:
            return None
        coroutine = self._application.bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return asyncio.run_coroutine_threadsafe(coroutine, self._loop)

