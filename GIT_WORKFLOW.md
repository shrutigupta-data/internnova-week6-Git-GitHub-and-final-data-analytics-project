# Git and GitHub Workflow

Run commands from the `week6_assignment_internnova` project directory. Create an empty GitHub repository first, for example `week6-assignment-internnova`, without initializing a README or license on GitHub.

## Initialize locally

```bash
cd /path/to/python-for-ai/week6_assignment_internnova
git init -b main
```

If a remote repository already exists, clone it instead of initializing a second repository:

```bash
git clone https://github.com/<YOUR-USERNAME>/week6-assignment-internnova.git
cd week6-assignment-internnova
```

## First commit and push

After reviewing the files and running both scripts:

```bash
git add .
git commit -m "Build student performance analytics capstone"
git remote add origin https://github.com/<YOUR-USERNAME>/week6-assignment-internnova.git
git push -u origin main
```

If `origin` is already configured, check it with `git remote -v` and skip `git remote add origin`.

## Three meaningful checkpoints

At minimum, keep three separate commits so the history shows the work developing:

```bash
git add data scripts requirements.txt .gitignore
git commit -m "Add validated student data preparation"

git add scripts/eda.py eda_findings.md descriptive_statistics.csv correlation_matrix.csv iqr_outliers.csv department_summary.csv visuals
git commit -m "Add exploratory analysis and visualizations"

git add README.md GIT_WORKFLOW.md insights.md presentation_outline.md powerbi
git commit -m "Document insights and Power BI dashboard"
git push
```

The first commit can instead be the single initial commit above; after it, make the next two checkpoints as meaningful work is completed. Do not commit virtual environments, credentials, or unrelated files.