# EDA Findings

## Dataset profile

- The cleaned dataset contains **24 students** across **4 departments**. It has no date field, so this analysis does not claim a time-based trend.
- The cohort average is **72.22/100**; average attendance is **85.83%**.
- **21 of 24 students (87.5%)** pass under the rule that every subject mark must be at least 40; **3** fail.

## Results and patterns

- **Engineering** has the highest department average (**78.46/100**, n=6); **Science** has the lowest (**65.79/100**, n=6) and a **50.0%** pass rate.
- The strongest subject by mean is **Computer Science (74.83)**; the weakest is **English (70.67)**, a difference of **4.17 points**.
- The Pearson correlation between attendance and student average marks is **0.966**. This is an association in a small synthetic cohort, not evidence that attendance causes higher marks.
- IQR screening flagged **0** observations across subject marks, attendance, and student averages. A zero count means no values crossed the 1.5-IQR fences; it does not prove that every record is error-free.

## Interpretation limits

The supplied file is a small synthetic cross-sectional dataset. Department differences are descriptive, not causal or necessarily representative of a real school. Because there is no date/term field, year-over-year or within-student change cannot be measured.
