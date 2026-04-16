import requests
import json
from datetime import datetime, timedelta

def get_user_stats(username):
    base_url = "https://api.github.com"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitTrack-App"
    }

    # Get user profile
    user_response = requests.get(f"{base_url}/users/{username}", headers=headers)
    user_data = user_response.json()

    # Get repositories
    repos_response = requests.get(
        f"{base_url}/users/{username}/repos?sort=updated&per_page=10",
        headers=headers
    )
    repos_data = repos_response.json()

    # Get recent events (commits, PRs, etc.)
    events_response = requests.get(
        f"{base_url}/users/{username}/events/public?per_page=30",
        headers=headers
    )
    events_data = events_response.json()

    # Count commits in last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_commits = 0
    commit_repos = {}

    for event in events_data:
        if event.get("type") == "PushEvent":
            event_date = datetime.strptime(
                event["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
            if event_date > seven_days_ago:
                commits_count = len(event["payload"].get("commits", []))
                recent_commits += commits_count
                repo_name = event["repo"]["name"].split("/")[1]
                commit_repos[repo_name] = commit_repos.get(repo_name, 0) + commits_count

    # Get language breakdown
    languages = {}
    for repo in repos_data:
        if isinstance(repo, dict) and repo.get("language"):
            lang = repo["language"]
            languages[lang] = languages.get(lang, 0) + 1

    stats = {
        "username": username,
        "name": user_data.get("name", username),
        "bio": user_data.get("bio", ""),
        "public_repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
        "recent_commits": recent_commits,
        "commit_repos": commit_repos,
        "languages": languages,
        "top_repos": [
            {
                "name": r["name"],
                "stars": r["stargazers_count"],
                "language": r.get("language", "N/A"),
                "description": r.get("description", "")
            }
            for r in repos_data
            if isinstance(r, dict)
        ][:5],
        "generated_at": datetime.now().strftime("%B %d, %Y at %I:%M %p")
    }

    return stats


if __name__ == "__main__":
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "shivain-gupta-827772346"
    stats = get_user_stats(username)
    print(json.dumps(stats, indent=2))
