# Presentation Outline

## Slide 1 - Project and question
- Week 6 Student Performance Analytics capstone
- Question: where do subject and department results suggest support may be useful?
- Scope: 24 synthetic student records; descriptive analysis only

## Slide 2 - Dataset and preparation
- Eight fields: student ID, name, department, four subject marks, attendance
- 0-100 measurement ranges; four departments with six students each
- No missing values, duplicate records, duplicate IDs, or date field in supplied data
- Explain the validation and missing-value policies in `data_prep.py`

## Slide 3 - Overall cohort results
- Cohort mean: 72.22/100
- 21 pass and 3 fail under the rule that every subject mark is at least 40
- Show score distribution and pass/fail composition

## Slide 4 - Subject patterns
- Computer science mean: 74.83; English mean: 70.67
- Show subject-mean comparison and subject boxplots
- No observations crossed the 1.5-IQR outlier fences

## Slide 5 - Department comparison
- Engineering mean: 78.46; Science mean: 65.79
- Science pass rate: 50%; other three departments: 100% in this sample
- Show department comparison; emphasize each department has only six records

## Slide 6 - Attendance and achievement
- Attendance mean: 85.83%
- Attendance/average-mark Pearson correlation: 0.966
- Association is not causation; sample is small, synthetic, and cross-sectional

## Slide 7 - Power BI report and recommendations
- KPI row: student count, average score, pass rate, average attendance
- Detail visuals: subject results, department results, student comparison, slicers
- Recommend a Science diagnostic and targeted English review based on item-level evidence

## Slide 8 - Limitations and conclusion
- No date/term field; no trend-over-time claims
- Validate with larger real data and educator input before operational decisions
- Reproducible Python outputs and Power BI build specification are included