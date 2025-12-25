"""
Personal finance analysis tool.

Provides data-driven summaries, budget structure hints, and savings recommendations
based on user-provided income, expense, and savings goal data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Income:
    fixed: List[float]
    variable: List[float]

    def total(self) -> float:
        return sum(self.fixed) + sum(self.variable)

    def breakdown(self) -> Dict[str, float]:
        return {
            "fixed": round(sum(self.fixed), 2),
            "variable": round(sum(self.variable), 2),
            "total": round(self.total(), 2),
        }


@dataclass
class Expense:
    category: str
    amount: float
    recurring: bool = True


@dataclass
class SavingsGoal:
    name: str
    target: float
    current: float

    def progress(self) -> float:
        if self.target == 0:
            return 0.0
        return min(round(self.current / self.target, 4), 1.0)


@dataclass
class FinanceData:
    income: Income
    expenses: List[Expense]
    one_time_expenses: List[Expense]
    savings_goals: List[SavingsGoal]
    current_balance: float
    period_months: int = 1


@dataclass
class BudgetSummary:
    total_income: float
    total_expenses: float
    net_cash_flow: float
    savings_rate: float
    fixed_costs: float
    variable_costs: float
    one_time_costs: float


@dataclass
class Insights:
    largest_categories: List[Tuple[str, float]]
    category_totals: Dict[str, float]
    rule_50_30_20: Dict[str, float]
    status_lights: Dict[str, str]


@dataclass
class Recommendations:
    actions: List[str]


@dataclass
class VisualizationData:
    expense_pie: Dict[str, float]
    income_vs_expenses: Dict[str, float]
    savings_progress: List[Dict[str, float]]


@dataclass
class AnalysisResult:
    summary: BudgetSummary
    insights: Insights
    recommendations: Recommendations
    visualization_data: VisualizationData


def build_finance_data(payload: Dict) -> FinanceData:
    income_data = payload.get("income", {})
    expenses_data = payload.get("expenses", [])
    one_time_data = payload.get("one_time_expenses", [])
    goals_data = payload.get("savings_goals", [])

    income = Income(
        fixed=income_data.get("fixed", []),
        variable=income_data.get("variable", []),
    )

    expenses = [
        Expense(category=item.get("category", "other"), amount=float(item.get("amount", 0)), recurring=item.get("recurring", True))
        for item in expenses_data
    ]

    one_time_expenses = [
        Expense(category=item.get("category", "other"), amount=float(item.get("amount", 0)), recurring=item.get("recurring", False))
        for item in one_time_data
    ]

    savings_goals = [
        SavingsGoal(name=item.get("name", "goal"), target=float(item.get("target", 0)), current=float(item.get("current", 0)))
        for item in goals_data
    ]

    return FinanceData(
        income=income,
        expenses=expenses,
        one_time_expenses=one_time_expenses,
        savings_goals=savings_goals,
        current_balance=float(payload.get("current_balance", 0)),
        period_months=int(payload.get("period_months", 1)),
    )


def summarize_budget(finance_data: FinanceData) -> BudgetSummary:
    fixed_expenses = sum(exp.amount for exp in finance_data.expenses if exp.recurring)
    variable_expenses = sum(exp.amount for exp in finance_data.expenses if not exp.recurring)
    one_time_costs = sum(exp.amount for exp in finance_data.one_time_expenses)

    total_income = finance_data.income.total()
    total_expenses = fixed_expenses + variable_expenses + one_time_costs
    net_cash_flow = total_income - total_expenses
    savings_rate = 0.0 if total_income == 0 else round(max(net_cash_flow, 0) / total_income, 4)

    return BudgetSummary(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_cash_flow=round(net_cash_flow, 2),
        savings_rate=savings_rate,
        fixed_costs=round(fixed_expenses, 2),
        variable_costs=round(variable_expenses, 2),
        one_time_costs=round(one_time_costs, 2),
    )


def categorize_expenses(expenses: List[Expense]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for exp in expenses:
        totals[exp.category] = round(totals.get(exp.category, 0) + exp.amount, 2)
    return totals


def compute_rule_50_30_20(total_income: float) -> Dict[str, float]:
    return {
        "needs": round(total_income * 0.5, 2),
        "wants": round(total_income * 0.3, 2),
        "savings": round(total_income * 0.2, 2),
    }


def build_status_lights(summary: BudgetSummary, category_totals: Dict[str, float]) -> Dict[str, str]:
    lights: Dict[str, str] = {}
    income = summary.total_income

    if income == 0:
        lights["savings_rate"] = "red"
    elif summary.savings_rate >= 0.2:
        lights["savings_rate"] = "green"
    elif summary.savings_rate >= 0.1:
        lights["savings_rate"] = "yellow"
    else:
        lights["savings_rate"] = "red"

    housing = category_totals.get("miete", category_totals.get("wohnen", 0))
    if income == 0:
        lights["housing_load"] = "red"
    else:
        ratio = housing / income
        lights["housing_load"] = "green" if ratio <= 0.3 else "yellow" if ratio <= 0.4 else "red"

    return lights


def derive_recommendations(summary: BudgetSummary, insights: Insights, finance_data: FinanceData) -> Recommendations:
    actions: List[str] = []

    if summary.net_cash_flow < 0:
        actions.append("Netto ist negativ: Variable Ausgaben um 10-15% senken und Einmalposten prüfen.")
    elif summary.savings_rate < 0.1:
        actions.append("Sparquote unter 10%: Daueraufträge für Rücklagen unmittelbar nach Gehaltseingang einrichten.")

    for category, amount in insights.largest_categories:
        share = amount / summary.total_income if summary.total_income else 0
        if share > 0.15 and category not in {"miete", "wohnen"}:
            actions.append(f"Kategorie '{category}' liegt bei {share:.0%} des Einkommens: monatliches Budgetlimit setzen.")

    subscription_heavy = any("abo" in exp.category.lower() or "subscription" in exp.category.lower() for exp in finance_data.expenses)
    if subscription_heavy:
        actions.append("Abos bündeln oder kündigen: Streaming/Software-Angebote vergleichen.")

    goals_incomplete = [goal for goal in finance_data.savings_goals if goal.progress() < 1.0]
    for goal in goals_incomplete:
        monthly_needed = (goal.target - goal.current) / max(finance_data.period_months, 1)
        actions.append(
            f"Ziel '{goal.name}': monatlich ca. {monthly_needed:.2f} zurücklegen, um innerhalb von {finance_data.period_months} Monat(en) das Ziel zu erreichen."
        )

    if not actions:
        actions.append("Budget ist im grünen Bereich: Überschüsse automatisiert investieren oder Rücklagen ausbauen.")

    return Recommendations(actions=actions)


def build_visualization_data(summary: BudgetSummary, insights: Insights, finance_data: FinanceData) -> VisualizationData:
    savings_progress = [
        {
            "name": goal.name,
            "progress": goal.progress(),
            "current": goal.current,
            "target": goal.target,
        }
        for goal in finance_data.savings_goals
    ]

    income_vs_expenses = {
        "income": summary.total_income,
        "expenses": summary.total_expenses,
        "net": summary.net_cash_flow,
    }

    return VisualizationData(
        expense_pie=insights.category_totals,
        income_vs_expenses=income_vs_expenses,
        savings_progress=savings_progress,
    )


def analyze_finances(payload: Dict) -> AnalysisResult:
    finance_data = build_finance_data(payload)
    summary = summarize_budget(finance_data)

    all_expenses = finance_data.expenses + finance_data.one_time_expenses
    category_totals = categorize_expenses(all_expenses)
    largest_categories = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[:3]
    rule_50_30_20 = compute_rule_50_30_20(summary.total_income)
    status_lights = build_status_lights(summary, category_totals)

    insights = Insights(
        largest_categories=largest_categories,
        category_totals=category_totals,
        rule_50_30_20=rule_50_30_20,
        status_lights=status_lights,
    )

    recommendations = derive_recommendations(summary, insights, finance_data)
    visualization_data = build_visualization_data(summary, insights, finance_data)

    return AnalysisResult(
        summary=summary,
        insights=insights,
        recommendations=recommendations,
        visualization_data=visualization_data,
    )


def format_summary(result: AnalysisResult) -> str:
    lines = [
        "Kurzüberblick:",
        f"- Einnahmen: {result.summary.total_income:.2f}",
        f"- Ausgaben: {result.summary.total_expenses:.2f}",
        f"- Netto: {result.summary.net_cash_flow:.2f}",
        f"- Sparquote: {result.summary.savings_rate:.1%}",
    ]

    lines.append("\nTop-Kategorien:")
    for category, amount in result.insights.largest_categories:
        lines.append(f"- {category}: {amount:.2f}")

    lines.append("\nEmpfehlungen:")
    for idx, action in enumerate(result.recommendations.actions, start=1):
        lines.append(f"{idx}. {action}")

    return "\n".join(lines)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python financial_analysis.py <data.json>")

    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    result = analyze_finances(payload)
    print(format_summary(result))
