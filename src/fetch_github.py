import json
import sys
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
    """GET a GitHub API endpoint and raise a useful error on failure."""
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def get_recent_activity(username, days=7):
    """Return public push activity from the last `days` days.

    GitHub returns events in reverse chronological order. We paginate until
    events are older than the requested window or MAX_EVENT_PAGES is reached.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent_commits = 0
    commit_repos = {}
    pages_checked = 0

    for page in range(1, MAX_EVENT_PAGES + 1):
        events = github_get(
            f"{BASE_URL}/users/{username}/events/public",
            params={"per_page": 100, "page": page},
        )
        pages_checked += 1

        if not events:
            break

        reached_cutoff = False

        for event in events:
            created_at = event.get("created_at")
            if not created_at:
                continue

            event_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            if event_date < cutoff:
                reached_cutoff = True
                break

            if event.get("type") != "PushEvent":
                continue

            commits = event.get("payload", {}).get("commits") or []
            commit_count = len(commits)
            recent_commits += commit_count

            repo_full_name = event.get("repo", {}).get("name", "")
            repo_name = repo_full_name.split("/", 1)[-1] if repo_full_name else "Unknown"
            commit_repos[repo_name] = commit_repos.get(repo_name, 0) + commit_count

        if reached_cutoff or len(events) < 100:
            break

    return recent_commits, commit_repos, pages_checked


def get_user_stats(username):
    user_data = github_get(f"{BASE_URL}/users/{username}")

    repos_data = github_get(
        f"{BASE_URL}/users/{username}/repos",
        params={
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
            "type": "owner",
        },
    )

    recent_commits, commit_repos, event_pages = get_recent_activity(username)

    # Count repositories by their primary language.
    languages = {}
    for repo in repos_data:
        language = repo.get("language")
        if language:
            languages[language] = languages.get(language, 0) + 1

    # Select the five repositories with the highest star count.
    top_repos = sorted(
        [repo for repo in repos_data if isinstance(repo, dict)],
        key=lambda repo: (
            repo.get("stargazers_count", 0),
            repo.get("forks_count", 0),
            repo.get("updated_at", ""),
        ),
        reverse=True,
    )[:5]

    stats = {
        "username": username,
        "name": user_data.get("name") or username,
        "bio": user_data.get("bio") or "",
        "public_repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
        "recent_commits": recent_commits,
        "commit_repos": dict(
            sorted(commit_repos.items(), key=lambda item: item[1], reverse=True)
        ),
        "languages": dict(
            sorted(languages.items(), key=lambda item: item[1], reverse=True)
        ),
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
        "event_pages": event_pages,
        "generated_at": datetime.now().astimezone().strftime("%B %d, %Y at %I:%M %p %Z"),
    }

    return stats


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Shivain-codes"

    try:
        stats = get_user_stats(username)
        print(json.dumps(stats, indent=2))
    except requests.RequestException as exc:
        print(f"GitHub API request failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Could not process GitHub response: {exc}", file=sys.stderr)
        sys.exit(1)
