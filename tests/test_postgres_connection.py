
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from datapilot.connectors.sql import connection


def test_requires_postgres_url(monkeypatch):
    settings = MagicMock()
    settings.postgres_url = None
    monkeypatch.setattr(
        connection, "get_settings", lambda: settings
    )

    connection.get_postgres_engine.cache_clear()
    try:
        with pytest.raises(ValueError, match="PostgreSQL URL"):
            connection.get_postgres_engine()
    finally:
        connection.get_postgres_engine.cache_clear()


def test_creates_engine_with_safe_pool_settings(monkeypatch):
    settings = MagicMock()
    settings.postgres_url = SecretStr(
        "postgresql+psycopg://user:pass@localhost:5432/test"
    )
    monkeypatch.setattr(
        connection, "get_settings", lambda: settings
    )

    expected_engine = MagicMock()
    create_engine_mock = MagicMock(return_value=expected_engine)
    monkeypatch.setattr(connection, "create_engine", create_engine_mock)

    connection.get_postgres_engine.cache_clear()
    try:
        engine = connection.get_postgres_engine()

        assert engine is expected_engine
        kwargs = create_engine_mock.call_args.kwargs
        assert kwargs["pool_pre_ping"] is True
        assert kwargs["hide_parameters"] is True
        assert kwargs["pool_size"] == 5
        assert kwargs["max_overflow"] == 5
    finally:
        connection.get_postgres_engine.cache_clear()


def test_adapter_uses_shared_engine(monkeypatch):
    expected_engine = MagicMock()
    monkeypatch.setattr(
        connection,
        "get_postgres_engine",
        lambda: expected_engine,
    )

    adapter = connection.get_postgres_adapter()

    assert adapter.engine is expected_engine
    assert adapter.source_type == "postgresql"
