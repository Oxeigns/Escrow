import asyncio
import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch


class WebhookTests(unittest.TestCase):
    def test_executor_runs_outside_loop_and_initializes_before_webhook(self):
        aiogram = ModuleType('aiogram')
        aiogram.Bot = object
        aiogram.Dispatcher = object
        executor = ModuleType('aiogram.utils.executor')
        cfg = SimpleNamespace(WEBHOOK_HOST='https://example.org', WEBHOOK_PATH='/hook',
                              WEBAPP_HOST='0.0.0.0', WEBAPP_PORT=8080)
        config = ModuleType('bot.config')
        config.load_config = lambda: cfg
        seen = []
        bot = SimpleNamespace(set_webhook=AsyncMock())
        async def startup(dp):
            seen.append('initialized')
        async def shutdown(dp):
            pass
        def start_webhook(**kwargs):
            with self.assertRaises(RuntimeError):
                asyncio.get_running_loop()
            asyncio.run(kwargs['on_startup'](None))
            self.assertEqual(seen, ['initialized'])
            self.assertIs(kwargs['on_shutdown'], shutdown)
        executor.start_webhook = start_webhook
        with patch.dict(sys.modules, {'aiogram': aiogram, 'aiogram.utils.executor': executor,
                                      'bot.config': config}):
            spec = importlib.util.spec_from_file_location('webhook_under_test',
                Path(__file__).resolve().parents[1] / 'webhooks/handler.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.run_webhook(bot, None, on_startup=startup, on_shutdown=shutdown)
        bot.set_webhook.assert_awaited_once_with('https://example.org/hook', drop_pending_updates=True)
