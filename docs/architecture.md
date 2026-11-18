# Architecture

```
 data/expenses.csv  (manual entries / CSV export / synthetic data)
          |
          v
 +--------------------+     +-----------------------+
 | data_generator.py  |     | data_loader.py        |
 | (optional: makes   | --> | read CSV, fix types,  |
 |  fake data)        |     | clean, standardise    |
 +--------------------+     +-----------+-----------+
                                        |  clean DataFrame
                                        v
                            +-----------------------+
                            | analysis.py           |
                            | KPIs, category, month,|
                            | payment, daily,       |
                            | budget check, insights|
                            +-----+-------------+---+
                                  |             |
                 tables / text    v             v   charts
                       +---------------+   +----------------+
                       | report.py     |   | visualize.py   |
                       | outputs/*.csv |   | images/*.png   |
                       | reports/*.txt |   | (Matplotlib +  |
                       +---------------+   |  Seaborn)      |
                                           +----------------+
 main.py runs all steps in order.
 app_streamlit.py (optional) shows the same analysis in a web dashboard.
```

## Data flow

1. **Input**: `date, category, amount, payment_method, description`
2. **Cleaning**: wrong types and invalid rows removed, spelling standardised,
   duplicates dropped (every fix is counted in a log).
3. **Analysis**: functions in `analysis.py` take the clean table and return
   numbers or small tables. They never print or plot.
4. **Output**: `report.py` writes CSV tables and a text report;
   `visualize.py` draws four charts.

## Design choices

- **One job per file** keeps the code easy to read, test and explain.
- **Plot functions return a Figure** so the same code feeds PNG files and Streamlit.
- **Partial months are detected**, so an unfinished month is never compared
  unfairly with full months.
