"""Generate reproducible EDA tables, findings, and labeled charts."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned" / "students_cleaned.csv"
VISUALS_PATH = PROJECT_ROOT / "visuals"
SUBJECT_COLUMNS = ["english", "mathematics", "science", "computer_science"]
NUMERIC_COLUMNS = [*SUBJECT_COLUMNS, "attendance"]


def load_analysis_data() -> pd.DataFrame:
    """Load the prepared data and derive consistent student-level metrics."""
    data = pd.read_csv(CLEAN_PATH)
    data["average_marks"] = data[SUBJECT_COLUMNS].mean(axis=1)
    data["result"] = data[SUBJECT_COLUMNS].ge(40).all(axis=1).map(
        {True: "Pass", False: "Fail"}
    )
    return data


def make_charts(data: pd.DataFrame, department_summary: pd.DataFrame) -> None:
    """Save six distinct chart types with explicit titles and axis labels."""
    VISUALS_PATH.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="deep")

    subject_means = data[SUBJECT_COLUMNS].mean()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.lineplot(x=subject_means.index, y=subject_means.values, marker="o", ax=ax)
    ax.set(title="Average Marks Across Subjects", xlabel="Subject", ylabel="Mean mark (0-100)")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(VISUALS_PATH / "subject_mean_trend.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=department_summary, x="department", y="average_marks", ax=ax)
    ax.set(title="Average Student Score by Department", xlabel="Department", ylabel="Mean student score (0-100)")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(VISUALS_PATH / "department_comparison.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=data, x="average_marks", bins=8, kde=True, ax=ax)
    ax.set(title="Distribution of Student Average Marks", xlabel="Student average mark (0-100)", ylabel="Number of students")
    fig.tight_layout()
    fig.savefig(VISUALS_PATH / "score_distribution.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot(data=data, x="attendance", y="average_marks", ci=None, ax=ax)
    ax.set(title="Attendance and Student Average Marks", xlabel="Attendance (%)", ylabel="Student average mark (0-100)")
    fig.tight_layout()
    fig.savefig(VISUALS_PATH / "attendance_vs_average.png", dpi=160)
    plt.close(fig)

    result_counts = data["result"].value_counts().reindex(["Pass", "Fail"], fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(x=result_counts.index, y=result_counts.values, ax=ax)
    ax.set(title="Student Pass/Fail Composition", xlabel="Outcome", ylabel="Number of students")
    fig.tight_layout()
    fig.savefig(VISUALS_PATH / "pass_fail_composition.png", dpi=160)
    plt.close(fig)

    long_scores = data.melt(
        id_vars="student_id", value_vars=SUBJECT_COLUMNS,
        var_name="subject", value_name="mark",
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=long_scores, x="subject", y="mark", ax=ax)
    ax.set(title="Score Spread and Outliers by Subject", xlabel="Subject", ylabel="Mark (0-100)")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(VISUALS_PATH / "subject_score_boxplots.png", dpi=160)
    plt.close(fig)


def main() -> None:
    data = load_analysis_data()
    VISUALS_PATH.mkdir(parents=True, exist_ok=True)

    # Save numeric summaries separately from the categorical columns.
    data[NUMERIC_COLUMNS + ["average_marks"]].describe().to_csv(
        PROJECT_ROOT / "descriptive_statistics.csv"
    )
    correlation = data[NUMERIC_COLUMNS + ["average_marks"]].corr(numeric_only=True)
    correlation.to_csv(PROJECT_ROOT / "correlation_matrix.csv")

    outlier_rows = []
    for column in NUMERIC_COLUMNS + ["average_marks"]:
        q1 = data[column].quantile(0.25)
        q3 = data[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        for _, row in data.loc[~data[column].between(lower_bound, upper_bound)].iterrows():
            outlier_rows.append(
                {"student_id": row["student_id"], "column": column,
                 "value": row[column], "lower_bound": lower_bound,
                 "upper_bound": upper_bound}
            )
    pd.DataFrame(
        outlier_rows,
        columns=["student_id", "column", "value", "lower_bound", "upper_bound"],
    ).to_csv(PROJECT_ROOT / "iqr_outliers.csv", index=False)

    department_summary = (
        data.groupby("department", as_index=False)
        .agg(
            students=("student_id", "nunique"),
            average_marks=("average_marks", "mean"),
            pass_count=("result", lambda values: values.eq("Pass").sum()),
            pass_rate_pct=("result", lambda values: values.eq("Pass").mean() * 100),
            average_attendance=("attendance", "mean"),
        )
        .sort_values("average_marks", ascending=False)
    )
    department_summary.to_csv(PROJECT_ROOT / "department_summary.csv", index=False)

    subject_means = data[SUBJECT_COLUMNS].mean()
    pass_count = int(data["result"].eq("Pass").sum())
    fail_count = len(data) - pass_count
    weakest_subject = subject_means.idxmin().replace("_", " ").title()
    strongest_subject = subject_means.idxmax().replace("_", " ").title()
    weakest_department = department_summary.iloc[-1]
    strongest_department = department_summary.iloc[0]
    attendance_correlation = data[["attendance", "average_marks"]].corr().iloc[0, 1]
    outlier_count = len(outlier_rows)

    findings = f"""# EDA Findings

## Dataset profile

- The cleaned dataset contains **{len(data)} students** across **{data['department'].nunique()} departments**. It has no date field, so this analysis does not claim a time-based trend.
- The cohort average is **{data['average_marks'].mean():.2f}/100**; average attendance is **{data['attendance'].mean():.2f}%**.
- **{pass_count} of {len(data)} students ({pass_count / len(data) * 100:.1f}%)** pass under the rule that every subject mark must be at least 40; **{fail_count}** fail.

## Results and patterns

- **{strongest_department['department']}** has the highest department average (**{strongest_department['average_marks']:.2f}/100**, n={int(strongest_department['students'])}); **{weakest_department['department']}** has the lowest (**{weakest_department['average_marks']:.2f}/100**, n={int(weakest_department['students'])}) and a **{weakest_department['pass_rate_pct']:.1f}%** pass rate.
- The strongest subject by mean is **{strongest_subject} ({subject_means.max():.2f})**; the weakest is **{weakest_subject} ({subject_means.min():.2f})**, a difference of **{subject_means.max() - subject_means.min():.2f} points**.
- The Pearson correlation between attendance and student average marks is **{attendance_correlation:.3f}**. This is an association in a small synthetic cohort, not evidence that attendance causes higher marks.
- IQR screening flagged **{outlier_count}** observations across subject marks, attendance, and student averages. A zero count means no values crossed the 1.5-IQR fences; it does not prove that every record is error-free.

## Interpretation limits

The supplied file is a small synthetic cross-sectional dataset. Department differences are descriptive, not causal or necessarily representative of a real school. Because there is no date/term field, year-over-year or within-student change cannot be measured.
"""
    (PROJECT_ROOT / "eda_findings.md").write_text(findings, encoding="utf-8")
    make_charts(data, department_summary)

    print(f"Analyzed {len(data)} students; overall mean: {data['average_marks'].mean():.2f}")
    print(f"Pass/fail: {pass_count}/{fail_count}; attendance-score correlation: {attendance_correlation:.3f}")
    print(f"IQR outlier observations: {outlier_count}")
    print("Saved descriptive_statistics.csv, correlation_matrix.csv, iqr_outliers.csv,")
    print("department_summary.csv, eda_findings.md, and six charts in visuals/.")


if __name__ == "__main__":
    main()