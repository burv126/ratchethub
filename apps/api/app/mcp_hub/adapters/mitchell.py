"""Mitchell PMS adapter."""

from __future__ import annotations

from app.mcp_hub.adapters.base import BaseAdapter
from app.mcp_hub.enums import AuthMethod, IntegrationCategory, IntegrationProvider


class MitchellAdapter(BaseAdapter):
    provider = IntegrationProvider.MITCHELL
    display_name = "Mitchell"
    description = 'Управление автосервисом Mitchell — сметы, заказ-наряды и клиенты.'
    category = IntegrationCategory.PMS
    auth_method = AuthMethod.API_KEY
    api_version = "v1"
    capabilities = ["customers.read", "vehicles.read", "repair_orders.read", "estimates.read"]
    required_scopes = ["shop.read"]
    credential_fields = ["api_key"]
    docs_url = "https://www.mitchell.com"
    tool_defs = [
        (
            "mitchell.list_customers",
            'Список клиентов Mitchell',
            {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}},
            ["pms", "read"],
        ),
        (
            "mitchell.get_repair_order",
            'Получить заказ-наряд по ID',
            {"type": "object", "properties": {"repair_order_id": {"type": "string"}}, "required": ["repair_order_id"]},
            ["pms", "read"],
        ),
        (
            "mitchell.get_estimate",
            'Получить смету по ID',
            {"type": "object", "properties": {"estimate_id": {"type": "string"}}, "required": ["estimate_id"]},
            ["pms", "read"],
        ),
    ]
