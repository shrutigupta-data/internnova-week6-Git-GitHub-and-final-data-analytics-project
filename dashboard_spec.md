# Power BI Dashboard Build Specification

## 1. Load and clean the CSV

In Power BI Desktop, choose **Get Data > Text/CSV**, select `data/raw/students.csv`, then choose **Transform Data > Advanced Editor**. Replace the placeholder path below with the full path to that file on your computer. The query trims identity fields, converts invalid numeric text to null, removes records with invalid identity fields or out-of-range values, fills missing measures by department median (cohort median fallback), removes duplicate IDs, derives pass status, and unpivots the four subjects.

```powerquery
let
    FilePath = "C:\\path\\to\\week6_assignment_internnova\\data\\raw\\students.csv",
    Source = Csv.Document(
        File.Contents(FilePath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    RequiredColumns = {
        "student_id", "name", "department", "english", "mathematics",
        "science", "computer_science", "attendance"
    },
    Selected = Table.SelectColumns(Headers, RequiredColumns),
    TextCleaned = Table.TransformColumns(
        Selected,
        {
            {"student_id", each if _ = null then null else Text.Trim(Text.From(_)), type text},
            {"name", each if _ = null then null else Text.Trim(Text.From(_)), type text},
            {"department", each if _ = null then null else Text.Trim(Text.From(_)), type text}
        }
    ),
    NumericColumns = {"english", "mathematics", "science", "computer_science", "attendance"},
    NumericParsed = Table.TransformColumns(
        TextCleaned,
        List.Transform(NumericColumns, (column) =>
            {column, each try Number.From(_) otherwise null, type nullable number}
        )
    ),
    IdentityRows = Table.SelectRows(
        NumericParsed,
        each [student_id] <> null and [student_id] <> ""
            and [name] <> null and [name] <> ""
            and [department] <> null and [department] <> ""
    ),
    ExactDuplicatesRemoved = Table.Distinct(IdentityRows),
    ScoreColumns = {"english", "mathematics", "science", "computer_science"},
    InRange = Table.SelectRows(
        ExactDuplicatesRemoved,
        (row) => List.AllTrue(
            List.Transform(NumericColumns, (column) =>
                let value = Record.Field(row, column)
                in value = null or (value >= 0 and value <= 100)
            )
        )
    ),
    MedianOrFallback = (values as list, fallback as nullable number) as nullable number =>
        let Observed = List.RemoveNulls(values)
        in if List.IsEmpty(Observed) then fallback else List.Median(Observed),
    OverallMedians = Record.FromList(
        List.Transform(NumericColumns, (column) => MedianOrFallback(Table.Column(InRange, column), null)),
        NumericColumns
    ),
    DepartmentGroups = Table.Group(
        InRange,
        {"department"},
        {{"Rows", (group) =>
            let
                DepartmentMedians = Record.FromList(
                    List.Transform(NumericColumns, (column) =>
                        MedianOrFallback(Table.Column(group, column), Record.Field(OverallMedians, column))
                    ),
                    NumericColumns
                ),
                FillOperations = List.Transform(NumericColumns, (column) =>
                    {column, (value) =>
                        if value = null then Record.Field(DepartmentMedians, column) else value,
                        type nullable number
                    }
                ),
                Filled = Table.TransformColumns(group, FillOperations)
            in
                Filled
        }}
    ),
    Imputed = Table.Combine(DepartmentGroups[Rows]),
    UniqueStudents = Table.Distinct(Imputed, {"student_id"}),
    WithPassFlag = Table.AddColumn(
        UniqueStudents,
        "PassFlag",
        (row) => if List.AllTrue(List.Transform(ScoreColumns, (column) => Record.Field(row, column) >= 40)) then 1 else 0,
        Int64.Type
    ),
    Unpivoted = Table.Unpivot(WithPassFlag, ScoreColumns, "Subject", "Mark"),
    Renamed = Table.RenameColumns(Unpivoted, {{"student_id", "Student ID"}, {"name", "Student Name"}, {"department", "Department"}, {"attendance", "Attendance"}}),
    FinalTypes = Table.TransformColumnTypes(
        Renamed,
        {{"Student ID", type text}, {"Student Name", type text}, {"Department", type text}, {"Subject", type text}, {"Mark", type number}, {"Attendance", type number}, {"PassFlag", Int64.Type}}
    )
in
    FinalTypes
```

Name the query/table `StudentScores` and select **Close & Apply**. The supplied CSV is complete and valid, so its Power Query output should have 96 rows after unpivoting (24 students x 4 subjects), with no imputation or invalid-record removal. The Python clean file remains the reference output. If refreshing changed data, compare the transformed row counts and records with `scripts/data_prep.py`.

## 2. KPI card measures

Create these measures from **Modeling > New measure**. Because unpivoting repeats each student once per subject, use distinct student counts for student-level KPIs.

```DAX
Student Count = DISTINCTCOUNT(StudentScores[Student ID])

Average Student Score =
    AVERAGEX(
        VALUES(StudentScores[Student ID]),
        CALCULATE(AVERAGE(StudentScores[Mark]))
    )

Pass Rate =
    DIVIDE(
        CALCULATE(
            DISTINCTCOUNT(StudentScores[Student ID]),
            StudentScores[PassFlag] = 1
        ),
        [Student Count]
    )

Average Attendance = AVERAGE(StudentScores[Attendance])
```

Format `Average Student Score` and `Average Attendance` to one decimal place, and `Pass Rate` as a percentage.

## 3. Measures and additional visuals

```DAX
Average Subject Mark = AVERAGE(StudentScores[Mark])

Department Average Score = [Average Student Score]

Department Pass Rate = [Pass Rate]

Failing Students =
    CALCULATE(
        DISTINCTCOUNT(StudentScores[Student ID]),
        StudentScores[PassFlag] = 0
    )
```

Build at least these visuals:

1. **Subject comparison:** clustered column chart, `Subject` on the X-axis, `[Average Subject Mark]` as the value.
2. **Department performance:** bar chart, `Department` as the category and `[Department Average Score]` as the value.
3. **Pass rate by department:** column chart, `Department` on the X-axis and `[Department Pass Rate]` as the value; format as percentage.
4. **Attendance and achievement:** scatter chart using `Attendance` for X, `[Average Student Score]` for Y, `Student ID` in Details, and `Department` in Legend.
5. **Top students:** table with `Student Name`, `Department`, and `[Average Student Score]`; apply a visual-level Top N filter on student name using `[Average Student Score]` (for example, Top 10).

There is no date or term column, so a time-series visual or time slicer would be fabricated and should not be added. The subject comparison is the appropriate category-level alternative.

## 4. Slicers and layout

Suggested slicers: `Department`, `Subject`, `Student Name`, and `PassFlag` (display labels Pass/Fail if you create a corresponding text column). Keep the subject slicer relevant to subject-level visuals; student score and pass status remain student-level metrics.

Use a single-page 16:9 report. Put four KPI cards across the top (student count, average score, pass rate, average attendance). Place department performance and subject comparison in the middle row. Put attendance-versus-achievement scatter and the Top 10 student table in the lower row. Align the slicers in a compact left rail or top strip, use consistent 0-100 scales and percentage formatting, and include a small note that the data is a 24-record synthetic sample with no time field.