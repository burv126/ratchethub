"""Tekmetric PMS adapter."""

from __future__ import annotations

from app.mcp_hub.adapters.base import BaseAdapter
from app.mcp_hub.enums import AuthMethod, IntegrationCategory, IntegrationProvider


class TekmetricAdapter(BaseAdapter):
    provider = IntegrationProvider.TEKMETRIC
    display_name = "Tekmetric"
    description = 'Управление автосервисом — клиенты, автомобили и заказ-наряды.'
    category = IntegrationCategory.PMS
    auth_method = AuthMethod.API_KEY
    api_version = "v1"
    capabilities = ["customers.read", "vehicles.read", "repair_orders.read", "repair_orders.write"]
    required_scopes = ["shop.read", "shop.write"]
    credential_fields = ["api_key", "shop_id"]
    docs_url = "https://api.tekmetric.com"
    tool_defs = [
        (
            "tekmetric.list_customers",
            'Список клиентов Tekmetric',
            {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}},
            ["pms", "read"],
        ),
        (
            "tekmetric.get_repair_order",
            'Получить заказ-наряд по ID',
            {"type": "object", "properties": {"repair_order_id": {"type": "string"}}, "required": ["repair_order_id"]},
            ["pms", "read"],
        ),
        (
            "tekmetric.upsert_customer",
            'Создать или обновить клиента',
            {"type": "object", "properties": {"name": {"type": "string"}, "phone": {"type": "string"}}},
            ["pms", "write"],
        ),
    ]
