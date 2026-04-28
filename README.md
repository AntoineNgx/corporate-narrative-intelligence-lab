# Corporate Narrative Intelligence

A web-based portfolio demo that analyzes corporate annual report narratives and detects strategic narrative shifts over time.

The app demonstrates how unstructured corporate disclosure text can be transformed into decision signals: similarity changes, tone evolution, readability movement, topic shifts, abnormal change alerts, and links to leadership or financial events.

## Features

- Upload annual report narrative text by fiscal year.
- Enter ROA values and top management change events.
- Compare year-over-year narrative similarity, tone, readability, and topic movement.
- Flag abnormal narrative changes using a transparent scoring model.
- Inspect abnormal years with before/after excerpts and interpretation.
- Export a one-page HTML report.

## Out of Scope

- User authentication
- Live SEC scraping
- Paid data integration
- Full academic regression engine
- Real-time financial data
- Multi-user workspace
- Complex backend admin panel

## Project Structure

```text
corporate-narrative-intelligence/
  app/
    main.py
    pages/
      1_dashboard.py
      2_signal_detail.py
      3_methodology.py
      4_about.py
  data/
    raw/
      filings/
      financials.csv
      leadership_events.csv
    processed/
      filings_clean.csv
      textual_metrics.csv
      narrative_change.csv
      event_classification.csv
  models/
    preprocessing.py
    lm_tone.py
    finbert_sentiment.py
    readability.py
    similarity.py
    topics.py
    anomaly_detection.py
    event_classifier.py
  reports/
    sample_report_template.html
  notebooks/
    validation_demo.ipynb
  requirements.txt
  .env.example
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

## Demo Workflow

1. Open the landing page and launch the demo.
2. Upload annual filing text files, tag each with a fiscal year, and enter ROA data.
3. Add leadership events such as turnover, succession, or executive additions.
4. Review the dashboard for narrative stability, tone, readability, topic shifts, abnormal alerts, and event timing.
5. Click an abnormal year on the signal detail page to inspect excerpts and export an HTML report.

## Data Schema

The repo includes CSV placeholders that match the product specification:

- `companies`
- `filings`
- `textual_metrics`
- `narrative_change`
- `financial_metrics`
- `leadership_events`

For the demo, the app stores uploaded data in Streamlit session state and writes optional report output locally.

## Methodology

The app uses a hybrid model:

- Transparent lexical tone scoring based on finance-oriented positive, negative, and uncertainty dictionaries.
- Optional FinBERT-compatible sentiment placeholder with a deterministic fallback for offline demos.
- TF-IDF cosine similarity for year-over-year text stability.
- Gunning Fog readability scoring.
- TF-IDF keyword extraction for topic labels and topic shift approximation.
- Robust anomaly detection based on similarity drop, tone movement, readability movement, topic shift, ROA movement, and leadership-event proximity.

This is intended as a portfolio demo, not an investment, legal, or academic regression product.
