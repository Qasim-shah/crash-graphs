# Crash Graphs — Data Visualizer (Python)

This is a small tool to explore road crash data and turn it into clear charts. It reads local CSVs (and can fetch from public APIs) and saves visualizations so trends are easy to discuss.

What it does
- Loads crash data (from `data/` or an API)
- Cleans/filters the dataset for a given state/county/time range
- Produces plots (time trends, distributions, heatmaps) into `outputs/`

Stack and structure
- Python script(s) organized around small, testable functions
- Typical libraries: `pandas`, `matplotlib`/`seaborn`, `requests`
- Keeps file I/O simple: input in `data/`, results in `outputs/`

How I approached it
- Start with questions, not charts: “What pattern should this answer?”
- Favor readable plots with sane defaults over clever visuals
- Keep the pipeline simple so adding a new chart is a short function, not a refactor

Run (example)
```bash
python main.py  # saves figures to outputs/
```

Notes
- If you run this on a new machine, install the usual data stack: `pip install pandas matplotlib seaborn requests`.
- Data sources vary in shape, so the cleaning step stays defensive and explicit.
