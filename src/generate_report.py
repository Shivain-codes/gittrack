import json
import sys
import os
from fetch_github import get_user_stats


def generate_html(stats):
    # Build language bars
    lang_html = ""
    total_repos = sum(stats["languages"].values()) or 1
    colors = ["#4F86F7", "#1D9E75", "#E24B4A", "#EF9F27", "#7F77DD", "#D85A30"]

    for i, (lang, count) in enumerate(stats["languages"].items()):
        percentage = round((count / total_repos) * 100)
        color = colors[i % len(colors)]
        lang_html += f"""
        <div class="lang-row">
            <span class="lang-name">{lang}</span>
            <div class="lang-bar-track">
                <div class="lang-bar-fill" style="width:{percentage}%; background:{color};"></div>
            </div>
            <span class="lang-pct">{percentage}%</span>
        </div>"""

    # Build commit repos list
    commit_html = ""
    if stats["commit_repos"]:
        for repo, count in sorted(stats["commit_repos"].items(),
                                   key=lambda x: x[1], reverse=True):
            commit_html += f'<li><strong>{repo}</strong> — {count} commit{"s" if count > 1 else ""}</li>'
    else:
        commit_html = "<li>No commits in the last 7 days</li>"

    # Build top repos
    repos_html = ""
    for repo in stats["top_repos"]:
        desc = repo["description"] or "No description"
        repos_html += f"""
        <div class="repo-card">
            <div class="repo-name">{repo["name"]}</div>
            <div class="repo-desc">{desc}</div>
            <div class="repo-meta">
                <span class="repo-lang">{repo["language"]}</span>
                <span class="repo-stars">★ {repo["stars"]}</span>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitTrack — {stats["username"]}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f6f8fa; color: #24292e; padding: 2rem; }}
        .container {{ max-width: 860px; margin: 0 auto; }}
        .header {{ background: #24292e; color: white; border-radius: 12px;
                   padding: 2rem; margin-bottom: 1.5rem; }}
        .header h1 {{ font-size: 1.8rem; margin-bottom: 0.25rem; }}
        .header .bio {{ opacity: 0.7; font-size: 0.9rem; margin-top: 0.5rem; }}
        .header .generated {{ opacity: 0.5; font-size: 0.8rem; margin-top: 1rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr);
                       gap: 1rem; margin-bottom: 1.5rem; }}
        .stat-card {{ background: white; border: 1px solid #e1e4e8;
                      border-radius: 8px; padding: 1.25rem; text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: 700; color: #0366d6; }}
        .stat-label {{ font-size: 0.8rem; color: #586069; margin-top: 0.25rem; }}
        .section {{ background: white; border: 1px solid #e1e4e8;
                    border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        .section h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem;
                       padding-bottom: 0.5rem; border-bottom: 1px solid #e1e4e8; }}
        .lang-row {{ display: flex; align-items: center; gap: 0.75rem;
                     margin-bottom: 0.6rem; }}
        .lang-name {{ width: 80px; font-size: 0.85rem; flex-shrink: 0; }}
        .lang-bar-track {{ flex: 1; height: 8px; background: #f1f3f5;
                           border-radius: 99px; overflow: hidden; }}
        .lang-bar-fill {{ height: 100%; border-radius: 99px; }}
        .lang-pct {{ font-size: 0.8rem; color: #586069; width: 36px;
                     text-align: right; }}
        .commit-list {{ list-style: none; }}
        .commit-list li {{ padding: 0.4rem 0; font-size: 0.9rem;
                           border-bottom: 1px solid #f1f3f5; }}
        .repo-card {{ border: 1px solid #e1e4e8; border-radius: 6px;
                      padding: 1rem; margin-bottom: 0.75rem; }}
        .repo-name {{ font-weight: 600; color: #0366d6; margin-bottom: 0.25rem; }}
        .repo-desc {{ font-size: 0.85rem; color: #586069; margin-bottom: 0.5rem; }}
        .repo-meta {{ display: flex; gap: 1rem; font-size: 0.8rem; color: #586069; }}
        .badge {{ display: inline-block; background: #0366d6; color: white;
                  font-size: 0.75rem; padding: 2px 10px; border-radius: 99px;
                  margin-bottom: 0.5rem; }}
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <div class="badge">GitTrack Report</div>
        <h1>{stats["name"] or stats["username"]}</h1>
        <div>@{stats["username"]}</div>
        <div class="bio">{stats["bio"] or ""}</div>
        <div class="generated">Generated automatically on {stats["generated_at"]}</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{stats["public_repos"]}</div>
            <div class="stat-label">Public Repos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats["recent_commits"]}</div>
            <div class="stat-label">Commits (7 days)</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats["followers"]}</div>
            <div class="stat-label">Followers</div>
        </div>
    </div>

    <div class="section">
        <h2>Languages used across repos</h2>
        {lang_html or "<p style='color:#586069;font-size:0.9rem;'>No language data available</p>"}
    </div>

    <div class="section">
        <h2>Recent commits (last 7 days)</h2>
        <ul class="commit-list">{commit_html}</ul>
    </div>

    <div class="section">
        <h2>Top repositories</h2>
        {repos_html or "<p style='color:#586069;font-size:0.9rem;'>No repositories found</p>"}
    </div>

</div>
</body>
</html>"""

    return html


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "shivain-gupta-827772346"
    print(f"Fetching stats for {username}...", file=sys.stderr)
    stats = get_user_stats(username)
    html = generate_html(stats)

    os.makedirs("reports", exist_ok=True)
    output_path = "reports/index.html"
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Report generated: {output_path}", file=sys.stderr)
