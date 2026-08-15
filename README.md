# GitTrack

Automated GitHub activity tracker that generates a daily HTML report of your GitHub stats and publishes it to GitHub Pages.

## Live Report

**[View Live Report →](https://shivain-codes.github.io/gittrack/)**

## What it does

- Fetches your GitHub profile, repositories, and public activity via the GitHub API
- Generates a clean HTML analytics dashboard
- Tracks 7, 30, and 90-day commit activity
- Tracks current and longest commit streaks
- Shows active repositories, pull-request events, issues, and language breakdown
- Automatically refreshes every day via GitHub Actions
- Publishes the generated dashboard to GitHub Pages

## Tech Stack

- Python 3.11
- GitHub REST API
- GitHub Actions
- GitHub Pages

## Run locally

```bash
pip install requests
cd src
python generate_report.py Shivain-codes
```

## GitHub Workflow used

- Feature branches for components
- Pull Requests with descriptions before merging
- GitHub Issues for task tracking
- GitHub Actions for automation
- GitHub Pages for deployment

## Certificate

Built as proof of knowledge for the Career Essentials in GitHub Professional Certificate (LinkedIn Learning × GitHub, April 2026).
