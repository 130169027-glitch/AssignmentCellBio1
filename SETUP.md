# Setup guide (for you, the instructor)

## 1. Create the repository
1. On GitHub, click **New repository** → name it (e.g. `cell-bio-reflection-assignment`).
2. Make it **Public** if students will fork it, or **Private** with
   them added as collaborators if you'd rather control access.
3. Upload all the files from this folder (README.md, SETUP.md,
   requirements.txt, `scripts/`, `.github/`, `submissions/`) to the repo —
   either drag-and-drop on the GitHub web UI, or:
   ```
   git init
   git add .
   git commit -m "Set up cell biology reflection assignment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/cell-bio-reflection-assignment.git
   git push -u origin main
   ```

## 2. Enable Actions (usually on by default)
Go to the repo's **Settings → Actions → General** and make sure
"Allow all actions and reusable workflows" is selected. That's the
switch that lets the similarity-checker run automatically on PRs.

## 3. Share the repo link with students
Point them to the README — it has the question and submission steps.
If your students aren't comfortable with forking/PRs, an easier path:
have them just create a branch directly in the repo (add them as
collaborators first) instead of forking.

## 4. What happens automatically
Every time a student opens a pull request that adds a file under
`submissions/`, the **Check Submission Similarity** GitHub Action
runs, compares that answer against everyone else's, and posts a
comment on the PR with a similarity report. You review flagged PRs,
then merge the ones that are fine.

## 5. Adjusting sensitivity
If you're getting too many or too few flags, open
`.github/workflows/check-similarity.yml` and change:
```
python scripts/check_similarity.py --threshold 0.75
```
Lower the number (e.g. `0.6`) to flag more pairs; raise it (e.g.
`0.85`) to only flag near-identical answers.

## 6. Running it yourself, locally, anytime
```
pip install -r requirements.txt
python scripts/check_similarity.py
```
This is useful right before grading, without waiting for a PR.
