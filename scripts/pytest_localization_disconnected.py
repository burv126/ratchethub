"""Opt-in pytest support for localization unit/validation tests without a DB.

Requires ENVIRONMENT=test and DATABASE_URL pointing at
postgresql+asyncpg://invalid:invalid@127.0.0.1:1/ru_localization_disconnected.
Not a substitute for database integration tests.
"""

import pytest


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    import asyncpg
    from sqlalchemy.engine import make_url
    from app.infrastructure.config import settings

    url = make_url(settings.database_url)
    if settings.environment != "test" or (url.host, url.port, url.database) != (
        "127.0.0.1", 1, "ru_localization_disconnected"
    ):
        raise pytest.UsageError("Localization unit tests require the explicit disconnected test database URL")

    async def disconnected(*args, **kwargs):
        raise ConnectionRefusedError("Database intentionally disconnected for localization unit tests")

    asyncpg.connect = disconnected
