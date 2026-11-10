"""Discover success patterns and propose optimizations (decide-only)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from uuid import UUID, uuid4

from app.agents.decisions.types import (
    OptimizationDecision,
    PatternDiscoveryDecision,
)
from app.learning.models.decision_result import SuccessPattern
from app.learning.store import LearningStorePort


class LearningOptimizer:
    """Find patterns and recommend improvements — never mutates workflows/rules."""

    def __init__(self, store: LearningStorePort) -> None:
        self._store = store

    async def analyze_success_pattern(
        self, shop_id: UUID, *, limit: int = 300
    ) -> dict[str, Any]:
        results = await self._store.list_results(shop_id, limit=limit)
        groups: dict[str, list[Any]] = defaultdict(list)
        for r in results:
            key = f"{r.decision_kind}:{r.outcome_kind.value}"
            groups[key].append(r)

        patterns: list[SuccessPattern] = []
        decisions: list[PatternDiscoveryDecision] = []
        for key, items in groups.items():
            if len(items) < 2:
                continue
            success_rate = sum(1 for i in items if i.success) / len(items)
            if success_rate < 0.5 and len(items) < 5:
                continue
            decision_kind = key.split(":", 1)[0]
            pattern = SuccessPattern(
                id=uuid4(),
                shop_id=shop_id,
                pattern_key=key,
                description=(
                    f"Результаты {decision_kind} по {key.split(':', 1)[1]} успешны в {success_rate * 100:.0f}% случаев (n={len(items)})"
                ),
                support_count=len(items),
                success_rate=round(success_rate, 4),
                decision_kinds=[decision_kind],
                signals={"outcome_kind": key.split(":", 1)[1]},
                confidence=min(0.95, 0.4 + len(items) * 0.05),
            )
            await self._store.save_pattern(pattern)
            patterns.append(pattern)
            decisions.append(
                PatternDiscoveryDecision(
                    pattern_key=pattern.pattern_key,
                    description=pattern.description,
                    support_count=pattern.support_count,
                    success_rate=pattern.success_rate,
                    confidence=pattern.confidence,
                    rationale=pattern.description,
                )
            )

        return {
            "shop_id": str(shop_id),
            "patterns": [p.to_dict() for p in patterns],
            "decisions": decisions,
            "count": len(patterns),
            "ai_actions_allowed": False,
        }

    async def optimize_recommendation(
        self,
        shop_id: UUID,
        *,
        target: str = "recommendations",
        limit: int = 300,
    ) -> dict[str, Any]:
        evaluation_hint = await self._store.list_results(shop_id, limit=limit)
        patterns = await self._store.list_patterns(shop_id, limit=20)
        suggestions: list[str] = []
        if patterns:
            top = patterns[0]
            suggestions.append(
                f"Использовать закономерность '{top.pattern_key}' (успешность={top.success_rate:.0%}, примеров={top.support_count})"
            )
        fails = [r for r in evaluation_hint if not r.success]
        if fails:
            common = max(
                {r.decision_kind for r in fails},
                key=lambda k: sum(1 for r in fails if r.decision_kind == k),
            )
            suggestions.append(
                f"Проверить неудачные решения '{common}' — предложить более безопасные обращения"
            )
        if not suggestions:
            suggestions.append('Соберите больше результатов перед оптимизацией')

        decision = OptimizationDecision(
            target=target,
            suggestions=suggestions,
            expected_impact="improved_decision_accuracy",
            requires_review=True,
            auto_apply=False,
            rationale='Предложения оптимизации цикла обучения (требуется проверка)',
        )
        return {
            "shop_id": str(shop_id),
            "decision": decision,
            "decisions": [decision],
            "suggestions": suggestions,
            "auto_apply": False,
            "ai_actions_allowed": False,
        }
