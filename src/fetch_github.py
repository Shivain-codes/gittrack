import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "GitTrack-App",
}
REQUEST_TIMEOUT = 15
MAX_EVENT_PAGES = 10


def github_get(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_public_events(username):
    events = []
    for page in range(1, MAX_EVENT_PAGES + 1):
        page_events = github_get(
            f"{BASE_URL}/users/{username}/events/public",
            params={"per_page": 100, "page": page},
        )
        if not page_events:
            break
        events.extend(page_events)
        if len(page_events) < 100:
            break
    return events


def event_datetime(event):
    value = event.get("created_at")
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def analyze_activity(events, days=90):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    daily_commits = defaultdict(int)
    commit_repos = defaultdict(int)
    weekday_commits = Counter()
    pull_requests = 0
    issues = 0
    issue_comments = 0
    pr_comments = 0
    push_dates = set()

    for event in events:
        event_date = event_datetime(event)
        if not event_date or event_date < cutoff:
            continue

        day = event_date.date().isoformat()
        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type == "PushEvent":
            commit_count = len(payload.get("commits") or [])
            daily_commits[day] += commit_count
            if commit_count:
                push_dates.add(event_date.date())
                weekday_commits[event_date.strftime("%A")] += commit_count
            repo_name = event.get("repo", {}).get("name", "").split("/", 1)[-1]
            if repo_name and commit_count:
                commit_repos[repo_name] += commit_count
        elif event_type == "PullRequestEvent" and payload.get("action") in {"opened", "closed", "reopened"}:
            pull_requests += 1
        elif event_type == "IssuesEvent" and payload.get("action") in {"opened", "closed", "reopened"}:
            issues += 1
        elif event_type == "IssueCommentEvent":
            issue_comments += 1
        elif event_type == "PullRequestReviewCommentEvent":
            pr_comments += 1

    def total_since(period_days):
        period_cutoff = now - timedelta(days=period_days)
        return sum(
            count
            for day, count in daily_commits.items()
            if datetime.fromisoformat(day).replace(tzinfo=timezone.utc) >= period_cutoff
        )

    streak = 0
    cursor = now.date()
    if cursor not in push_dates:
        cursor -= timedelta(days=1)
    while cursor in push_dates:
        streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 0
    current_streak = 0
    if push_dates:
        cursor = min(push_dates)
        end_date = max(push_dates)
        while cursor <= end_date:
            if cursor in push_dates:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0
            cursor += timedelta(days=1)

    most_productive_day = max(weekday_commits.items(), key=lambda item: item[1], default=("N/A", 0))
    most_active_repo = next(iter(sorted(commit_repos.items(), key=lambda item: item[1], reverse=True)), ("N/A", 0))

    return {
        "daily_commits": dict(sorted(daily_commits.items())),
        "weekly_commits": total_since(7),
        "monthly_commits": total_since(30),
        "ninety_day_commits": total_since(90),
        "commit_repos": dict(sorted(commit_repos.items(), key=lambda item: item[1], reverse=True)),
        "pull_requests": pull_requests,
        "issues": issues,
        "issue_comments": issue_comments,
        "pr_comments": pr_comments,
        "current_streak": streak,
        "longest_streak": longest_streak,
        "most_productive_day": most_productive_day[0],
        "most_productive_day_commits": most_productive_day[1],
        "most_active_repo": most_active_repo[0],
        "most_active_repo_commits": most_active_repo[1],
        "average_commits_per_week": round(total_since(90) / 13, 1),
        "tracked_events": len(events),
        "tracked_since": min((event_datetime(event) for event in events if event_datetime(event)), default=None),
    }


def get_user_stats(username):
    user_data = github_get(f"{BASE_URL}/users/{username}")
    repos_data = github_get(
        f"{BASE_URL}/users/{username}/repos",
        params={"sort": "updated", "direction": "desc", "per_page": 100, "type": "owner"},
    )

    events = fetch_public_events(username)
    activity = analyze_activity(events)

    languages = {}
    for repo in repos_data:
        language = repo.get("language")
        if language:
            languages[language] = languages.get(language, 0) + 1

    top_repos = sorted(
        [repo for repo in repos_data if isinstance(repo, dict)],
        key=lambda repo: (
            repo.get("stargazers_count", 0),
            repo.get("forks_count", 0),
            repo.get("updated_at", ""),
        ),
        reverse=True,
    )[:5]

    tracked_since = activity["tracked_since"]
    tracked_since_text = tracked_since.astimezone().strftime("%B %d, %Y") if tracked_since else "Unavailable"

    return {
        "username": username,
        "name": user_data.get("name") or username,
        "bio": user_data.get("bio") or "",
        "public_repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
        **activity,
        "tracked_since": tracked_since_text,
        "languages": dict(sorted(languages.items(), key=lambda item: item[1], reverse=True)),
        "top_repos": [
            {
                "name": repo.get("name", "Unknown"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language") or "N/A",
                "description": repo.get("description") or "",
            }
            for repo in top_repos
        ],
        "generated_at": datetime.now().astimezone().strftime("%B %d, %Y at %I:%M %p %Z"),
    }


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Shivain-codes"
    try:
        print(json.dumps(get_user_stats(username), indent=2, default=str))
    except requests.RequestException as exc:
        print(f"GitHub API request failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Could not process GitHub response: {exc}", file=sys.stderr)
        sys.exit(1)
