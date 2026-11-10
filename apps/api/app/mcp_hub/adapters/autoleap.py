"""AutoLeap PMS adapter."""

from __future__ import annotations

from app.mcp_hub.adapters.base import BaseAdapter
from app.mcp_hub.enums import AuthMethod, IntegrationCategory, IntegrationProvider


class AutoLeapAdapter(BaseAdapter):
    provider = IntegrationProvider.AUTOLEAP
    display_name = "AutoLeap"
    description = 'CRM и платформа рабочих процессов автосервиса.'
    category = IntegrationCategory.PMS
    auth_method = AuthMethod.BEARER
    api_version = "v1"
    capabilities = ["appointments.read", "estimates.read", "customers.read"]
    required_scopes = ["shop.read"]
    credential_fields = ["access_token"]
    docs_url = "https://www.autoleap.com"
    tool_defs = [
        (
            "autoleap.list_appointments",
            'Список записей',
            {"type": "object", "properties": {"day": {"type": "string"}}},
            ["pms", "read"],
        ),
        (
            "autoleap.get_estimate",
            'Получить смету',
            {"type": "object", "properties": {"estimate_id": {"type": "string"}}, "required": ["estimate_id"]},
            ["pms", "read"],
        ),
    ]
