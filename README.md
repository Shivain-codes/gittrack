# GitTrack

Automated GitHub activity tracker that generates a daily HTML report 
of your GitHub stats and deploys it to GitHub Pages using GitHub Actions.

## Live Report
**[View Live Report →](https://YOUR_USERNAME.github.io/gittrack)**

## What it does
- Fetches your GitHub profile, repos, and recent commits via the GitHub API
- Generates a clean HTML dashboard showing your activity
- Automatically runs every day at midnight UTC via GitHub Actions
- Deploys the report to GitHub Pages with zero manual work

## Tech Stack
- Python 3.11
- GitHub REST API (public, no auth needed)
- GitHub Actions (scheduled cron workflow)
- GitHub Pages (automated deployment)

## Run locally
pip install requests
cd src
python generate_report.py YOUR_GITHUB_USERNAME

## GitHub Workflow used
- Feature branches for every component
- Pull Requests with descriptions before merging
- GitHub Issues for task tracking
- GitHub Actions for CI/CD automation
- GitHub Pages for deployment

## Certificate
Built as proof of knowledge for the Career Essentials in 
GitHub Professional Certificate (LinkedIn Learning × GitHub, April 2026)
