"""Placeholder adapter for future integrations."""

from __future__ import annotations

from typing import Any

from app.mcp_hub.adapters.base import BaseAdapter
from app.mcp_hub.enums import AuthMethod, IntegrationCategory, IntegrationProvider
from app.mcp_hub.models import ConnectionCredentials, IntegrationConnection, InvokeRequest


class FutureAdapter(BaseAdapter):
    provider = IntegrationProvider.FUTURE
    display_name = 'Будущие интеграции'
    description = 'Место для будущих коннекторов MCP — регистрация через реестр центра.'
    category = IntegrationCategory.EXTENSIBILITY
    auth_method = AuthMethod.NONE
    api_version = "v0"
    capabilities = ["registry.extend"]
    required_scopes = []
    credential_fields = []
    available = True
    future = True
    tool_defs = [
        (
            "future.ping",
            'Проверка состояния будущих коннекторов',
            {"type": "object", "properties": {"name": {"type": "string"}}},
            ["future"],
        ),
    ]

    async def authenticate(self, credentials: ConnectionCredentials) -> ConnectionCredentials:
        credentials.method = AuthMethod.NONE
        credentials.access_token = "future-placeholder"
        return credentials

    async def test_connection(self, connection: IntegrationConnection) -> dict[str, Any]:
        return {"ok": True, "provider": "future", "message": 'Готово к регистрации'}

    async def invoke(
        self,
        connection: IntegrationConnection,
        request: InvokeRequest,
    ) -> dict[str, Any]:
        return {
            "provider": "future",
            "tool": request.tool or "future.ping",
            "status": "not_implemented",
            "message": 'Зарегистрируйте адаптер для включения',
            "arguments": request.arguments,
        }
