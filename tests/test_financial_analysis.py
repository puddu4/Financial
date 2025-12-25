import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from financial_analysis import (
    AnalysisResult,
    analyze_finances,
    build_finance_data,
    format_summary,
    summarize_budget,
    validate_finance_data,
)


@pytest.fixture
def sample_payload():
    with open("sample_data.json", "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_summary_numbers(sample_payload):
    finance_data = build_finance_data(sample_payload)
    summary = summarize_budget(finance_data)

    assert summary.total_income == 3000
    assert summary.total_expenses == 2000
    assert summary.net_cash_flow == 1000
    assert summary.savings_rate == pytest.approx(0.3333)
    assert summary.fixed_costs == 1400
    assert summary.variable_costs == 200
    assert summary.one_time_costs == 400


def test_insights_and_recommendations(sample_payload):
    result: AnalysisResult = analyze_finances(sample_payload)

    # Largest categories should include rent, vacation, and groceries in that order
    assert result.insights.largest_categories[0] == ("miete", 900)
    assert result.insights.largest_categories[1] == ("urlaub", 400)
    assert result.insights.largest_categories[2] == ("lebensmittel", 350)

    # 50/30/20 rule should match income
    assert result.insights.rule_50_30_20 == {"needs": 1500.0, "wants": 900.0, "savings": 600.0}

    # Status lights: good savings rate and acceptable housing load
    assert result.insights.status_lights["savings_rate"] == "green"
    assert result.insights.status_lights["housing_load"] == "green"

    # Recommendations should include subscription and savings goal advice
    assert any("Abos bündeln" in rec for rec in result.recommendations.actions)
    assert any("Notgroschen" in rec for rec in result.recommendations.actions)
    assert any("Reise" in rec for rec in result.recommendations.actions)


def test_visualization_payload_shapes(sample_payload):
    result = analyze_finances(sample_payload)

    assert set(result.visualization_data.income_vs_expenses.keys()) == {"income", "expenses", "net"}
    assert result.visualization_data.expense_pie.get("miete") == 900

    progress_entries = result.visualization_data.savings_progress
    assert len(progress_entries) == 2
    assert progress_entries[0]["name"] == "Notgroschen"
    assert progress_entries[0]["progress"] == pytest.approx(0.5)


def test_validation_rejects_negative_values(sample_payload):
    sample_payload["income"]["fixed"][0] = -100

    with pytest.raises(ValueError) as err:
        finance_data = build_finance_data(sample_payload)
        validate_finance_data(finance_data)

    assert "Einnahmen" in str(err.value)


def test_format_summary_contains_key_sections(sample_payload):
    result = analyze_finances(sample_payload)
    text = format_summary(result)

    assert "Kurzüberblick" in text
    assert "Einnahmen" in text and "Ausgaben" in text
    assert "Empfehlungen" in text
    assert "Notgroschen" in text or "Reise" in text
