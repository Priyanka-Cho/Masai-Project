# data_pipeline

Fixed Baseline Conversion Rate (Required)
**1 GBP = 105.50 INR**
This is artificial constant for reproducibility, not live API.
Formula: price_inr = price_gbp * 105.50

Decision Log:
- Scraped 5 pages (100 books) to meet >=60 requirement, real category from product breadcrumb to get >=3 categories
- Normalized schema: categories(category_id PK) -> books(category_id FK) for 3NF
- Queries demonstrate SELECT/WHERE, ORDER BY, LIMIT, DISTINCT, IN, BETWEEN, JOIN
