# Financial Analysis Toolkit

Dieses kleine Werkzeug analysiert persönliche Finanzdaten und liefert eine klare Budgetübersicht, Sparpotenziale und Vorschläge für Visualisierungen.

## Anforderungen
- Python 3.9+
- Pytest zum Ausführen der Tests (optional)

## Nutzung
1. Trage Deine Finanzdaten in einer JSON-Datei ein. Ein Beispiel findest Du in `sample_data.json`.
2. Führe die Analyse aus:
   ```bash
   python financial_analysis.py sample_data.json
   ```
3. Die Ausgabe enthält eine Kurzbeschreibung, Top-Ausgabenkategorien und priorisierte Empfehlungen.

Das Script validiert die Eingaben und bricht mit einer klaren Fehlermeldung ab, wenn z. B. negative Beträge oder ein ungültiger Zeitraum angegeben sind.

## Tests
Führe alle Tests mit:
```bash
pytest
```

## Datenschema (Beispiel)
```json
{
  "income": {"fixed": [2500], "variable": [500]},
  "expenses": [
    {"category": "miete", "amount": 900, "recurring": true},
    {"category": "lebensmittel", "amount": 350, "recurring": true}
  ],
  "one_time_expenses": [{"category": "urlaub", "amount": 400, "recurring": false}],
  "savings_goals": [{"name": "Notgroschen", "target": 3000, "current": 1500}],
  "current_balance": 2000,
  "period_months": 6
}
```
