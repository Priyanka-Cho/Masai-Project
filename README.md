# Masai-Project - Book ETL Pipeline

## Setup
pip install -r requirements.txt

## Module 1 - Data Pipeline (Done)
Fixed Conversion Rate: 1 GBP = 105.50 INR (project-defined constant, no API)
Run: python data_pipeline/main.py
Outputs: data_pipeline/catalog.db (normalized 2-table PK/FK), cleaned_books_final.csv

Cleaning Decisions:
- price_gbp extracted via regex float
- rating mapped One->1...Five->5
- in_stock bool from 'In stock' text
- median imputation if parsing fails
- price_inr = price_gbp * 105.50

## Module 2 - Analytics (next)
## Module 3 - GenAI (next)
