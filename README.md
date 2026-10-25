# Student Performance Analytics

## Project Title

Week 6: Git, GitHub & Final Data Analytics Project - Student Performance Analytics

## Project Overview

This capstone profiles a small student-performance dataset, validates and prepares the records, explores marks and attendance, produces charts, and specifies a Power BI report. Python scripts make the cleaning and analysis repeatable. The source records are synthetic and are intended for practice, not institutional decisions.

## Problem Statement

Summarize achievement and attendance by subject and department, identify where additional academic support may be useful, and communicate the findings in a form that can be explored in Power BI. The supplied data is cross-sectional, so it cannot answer questions about change over time.

## Dataset Description

The raw file is [`data/raw/students.csv`](data/raw/students.csv), copied from the earlier student-performance project. It contains 24 synthetic student records and eight columns: `student_id`, `name`, `department`, four subject marks (`english`, `mathematics`, `science`, `computer_science`), and `attendance`. Marks and attendance use a 0-100 scale. The source has no missing values, duplicate rows, duplicate IDs, or date/term column. Four departments are represented equally (six records each).

## Tools Used

- Python 3
- pandas for CSV handling, validation, summaries, and grouping
- matplotlib and seaborn for figures
- Power BI Desktop with Power Query M and DAX for the dashboard specification
- Git and GitHub for version control and submission

From this folder, create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Data Cleaning Process

Run `python scripts/data_prep.py`. The script prints the input shape, dtypes, and null counts, validates the required columns, and saves `data/cleaned/students_cleaned.csv`.

- `student_id`, `name`, and `department`: trim surrounding whitespace; remove records with blank or missing identity/category fields because they cannot be reliably identified or grouped.
- `english`, `mathematics`, `science`, `computer_science`, and `attendance`: coerce numeric values; replace missing or non-numeric values with the department median, falling back to the cohort median when the department has no observed value. Drop records with values outside the valid 0-100 range rather than silently correcting invalid measurements.
- Exact duplicate rows are removed. If a student ID still appears more than once, keep the first valid record so the key remains unique; review conflicting source records before using this rule on real institutional data.

On the supplied file, the checks find no missing values, invalid ranges, duplicates, or blank identity fields, so the cleaning step retains all 24 rows without imputation.

## EDA

Run `python scripts/eda.py` after data preparation. It writes `descriptive_statistics.csv`, `correlation_matrix.csv`, `iqr_outliers.csv`, `department_summary.csv`, and [`eda_findings.md`](eda_findings.md). The IQR screen uses 1.5 times the interquartile range. No date field is present, so the subject line chart compares categories and is not a time-series chart.

## Visualizations

Six labeled charts are generated in [`visuals/`](visuals/):

- `subject_mean_trend.png` - mean mark by subject
- `department_comparison.png` - mean student score by department
- `score_distribution.png` - distribution of student averages
- `attendance_vs_average.png` - attendance and average-mark relationship
- `pass_fail_composition.png` - pass/fail counts
- `subject_score_boxplots.png` - score spread and IQR outliers by subject

## Power BI Dashboard

Follow [`powerbi/dashboard_spec.md`](powerbi/dashboard_spec.md) to import the same raw CSV, apply Power Query transformations, add DAX measures, and arrange the report. The query reshapes subject marks into a long format for subject comparisons. The dataset has no date field, so no time slicer or time-series visual is specified.

## Key Insights

The cohort average is 72.22/100 and 21 of 24 students pass the all-subjects-at-least-40 rule. Engineering has the highest department average (78.46), while Science has the lowest (65.79) and the lowest pass rate (50%). Computer science has the highest subject mean (74.83); English is lowest (70.67). See [`insights.md`](insights.md) for the detailed findings and recommendations, and `eda_findings.md` for reproducible summary values.

## Business Recommendations

Prioritize a diagnostic review and targeted support for Science students, especially students below 40 in one or more subjects. Review English and mathematics assessment results to identify specific foundational topics for intervention. Treat attendance as a monitoring signal, not a causal explanation: its association with marks in this small synthetic sample needs validation with larger, real, longitudinal data.

## Conclusion

This project demonstrates a repeatable analysis workflow from raw CSV validation to documented findings, saved visualizations, and a Power BI build specification. The results are descriptive and practice-only. A real deployment should use a larger, quality-checked dataset with dates/terms, privacy controls, and stakeholder review. The [`presentation_outline.md`](presentation_outline.md) contains an eight-slide presentation plan.