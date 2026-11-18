# Notebooks

Put exploration notebooks here (for example `01_explore_expenses.ipynb`).
You can reuse the project code inside a notebook:

```python
import sys; sys.path.append("..")          # let the notebook find src/
from src import data_loader, analysis

df, log = data_loader.load_expenses()
analysis.category_summary(df)
```
