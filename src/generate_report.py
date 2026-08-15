import html
import os
import sys

from fetch_github import get_user_stats


def generate_html(stats):
    lang_html = ""
    total_repos = sum(stats["languages"].values()) or 1
    colors = ["#4F86F7", "#1D9E75", "#E24B4A", "#EF9F27", "#7F77DD", "#D85A30"]

    for i, (lang, count) in enumerate(stats["languages"].items()):
        percentage = round((count / total_repos) * 100)
        lang_html += f"""
        <div class="lang-row">
            <span class="lang-name">{html.escape(lang)}</span>
            <div class="lang-bar-track">
                <div class="lang-bar-fill" style="width:{percentage}%; background:{colors[i % len(colors)]};"></div>
            </div>
            <span class="lang-pct">{percentage}%</span>
        </div>"""

    commit_html = "".join(
        f'<li><strong>{html.escape(repo)}</strong> — {count} {"commit" if count == 1 else "commits"}</li>'
        for repo, count in stats["commit_repos"].items()
    ) or "<li>No commits detected in the tracked activity window</li>"

    repos_html = ""
    for repo in stats["top_repos"]:
        repos_html += f"""
        <div class="repo-card">
            <div class="repo-name">{html.escape(repo["name"])}</div>
            <div class="repo-desc">{html.escape(repo["description"] or "No description")}</div>
            <div class="repo-meta">
                <span>{html.escape(repo["language"])}</span>
                <span>★ {repo["stars"]}</span>
                <span>Forks {repo["forks"]}</span>
            </div>
        </div>"""

    username = html.escape(stats["username"])
    name = html.escape(stats["name"] or stats["username"])
    bio = html.escape(stats["bio"] or "")
    generated_at = html.escape(stats["generated_at"])

    daily_data = ",".join(
        f"{{x: '{html.escape(day)}', y: {count}}}"
        for day, count in stats["daily_commits"].items()
    )

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="GitTrack GitHub activity report for @{username}">
    <title>GitTrack — @{username}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f6f8fa; color: #24292e; padding: 2rem; }}
        .container {{ max-width: 980px; margin: 0 auto; }}
        .header {{ background: #24292e; color: white; border-radius: 14px;
                   padding: 2rem; margin-bottom: 1.5rem; }}
        .header h1 {{ font-size: 1.8rem; margin-bottom: 0.25rem; }}
        .header .bio {{ opacity: 0.7; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.5; }}
        .header .generated {{ opacity: 0.5; font-size: 0.8rem; margin-top: 1rem; }}
        .badge {{ display: inline-block; background: #0366d6; color: white;
                  font-size: 0.75rem; padding: 3px 10px; border-radius: 99px; margin-bottom: 0.6rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
        .stat-card {{ background: white; border: 1px solid #e1e4e8; border-radius: 9px; padding: 1.25rem; text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: 700; color: #0366d6; }}
        .stat-label {{ font-size: 0.8rem; color: #586069; margin-top: 0.25rem; }}
        .section {{ background: white; border: 1px solid #e1e4e8; border-radius: 9px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        .section h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e1e4e8; }}
        .section-note {{ color: #586069; font-size: 0.78rem; margin-top: 0.75rem; line-height: 1.5; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; }}
        .metric {{ background: #f6f8fa; border-radius: 8px; padding: 1rem; }}
        .metric-value {{ font-size: 1.5rem; font-weight: 700; }}
        .metric-label {{ color: #586069; font-size: 0.75rem; margin-top: 0.25rem; }}
        .lang-row {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem; }}
        .lang-name {{ width: 100px; font-size: 0.85rem; flex-shrink: 0; }}
        .lang-bar-track {{ flex: 1; height: 8px; background: #f1f3f5; border-radius: 99px; overflow: hidden; }}
        .lang-bar-fill {{ height: 100%; border-radius: 99px; }}
        .lang-pct {{ font-size: 0.8rem; color: #586069; width: 36px; text-align: right; }}
        .chart {{ width: 100%; height: 230px; }}
        .commit-list {{ list-style: none; }}
        .commit-list li {{ padding: 0.4rem 0; font-size: 0.9rem; border-bottom: 1px solid #f1f3f5; }}
        .repo-card {{ border: 1px solid #e1e4e8; border-radius: 7px; padding: 1rem; margin-bottom: 0.75rem; }}
        .repo-card:last-child {{ margin-bottom: 0; }}
        .repo-name {{ font-weight: 600; color: #0366d6; margin-bottom: 0.25rem; }}
        .repo-desc {{ font-size: 0.85rem; color: #586069; margin-bottom: 0.5rem; line-height: 1.4; }}
        .repo-meta {{ display: flex; gap: 1rem; font-size: 0.8rem; color: #586069; }}
        .footer {{ text-align: center; color: #586069; font-size: 0.75rem; margin-top: 1rem; }}
        @media (max-width: 700px) {{
            body {{ padding: 1rem; }}
            .stats-grid, .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .repo-meta {{ flex-wrap: wrap; gap: 0.5rem 1rem; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="badge">GitTrack Analytics</div>
        <h1>{name}</h1>
        <div>@{username}</div>
        <div class="bio">{bio}</div>
        <div class="generated">Generated automatically on {generated_at}</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card"><div class="stat-number">{stats["public_repos"]}</div><div class="stat-label">Public Repos</div></div>
        <div class="stat-card"><div class="stat-number">{stats["weekly_commits"]}</div><div class="stat-label">Commits / 7 Days</div></div>
        <div class="stat-card"><div class="stat-number">{stats["monthly_commits"]}</div><div class="stat-label">Commits / 30 Days</div></div>
        <div class="stat-card"><div class="stat-number">{stats["current_streak"]}</div><div class="stat-label">Current Streak</div></div>
    </div>

    <div class="section">
        <h2>Activity overview</h2>
        <div class="metric-grid">
            <div class="metric"><div class="metric-value">{stats["longest_streak"]}</div><div class="metric-label">Longest tracked streak</div></div>
            <div class="metric"><div class="metric-value">{stats["pull_requests"]}</div><div class="metric-label">PR events</div></div>
            <div class="metric"><div class="metric-value">{stats["issues"]}</div><div class="metric-label">Issue events</div></div>
            <div class="metric"><div class="metric-value">{stats["ninety_day_commits"]}</div><div class="metric-label">Commits / 90 days</div></div>
        </div>
        <p class="section-note">Activity is based on public GitHub events currently available to the tracker. Tracked event history begins around {html.escape(stats["tracked_since"])}.</p>
    </div>

    <div class="section">
        <h2>Commit activity — tracked 90 days</h2>
        <div id="chart" class="chart"></div>
    </div>

    <div class="section">
        <h2>Languages across repositories</h2>
        {lang_html or "<p class='section-note'>No language data available.</p>"}
    </div>

    <div class="section">
        <h2>Most active repositories</h2>
        <ul class="commit-list">{commit_html}</ul>
    </div>

    <div class="section">
        <h2>Top repositories by stars</h2>
        {repos_html or "<p class='section-note'>No repositories found.</p>"}
    </div>

    <div class="footer">GitTrack • Generated by GitHub Actions</div>
</div>

<script>
const data = [{daily_data}];
const chart = document.getElementById('chart');
if (!data.length) {{
    chart.innerHTML = '<p class="section-note">No commit activity available in the tracked window.</p>';
}} else {{
    const width = chart.clientWidth || 800;
    const height = 230;
    const padding = 35;
    const max = Math.max(...data.map(d => d.y), 1);
    const x = i => padding + (i * (width - padding * 2) / Math.max(data.length - 1, 1));
    const y = value => height - padding - (value / max) * (height - padding * 2);
    const points = data.map((d, i) => `${{x(i)}},${{y(d.y)}}`).join(' ');
    chart.innerHTML = `<svg width="100%" height="${{height}}" viewBox="0 0 ${{width}} ${{height}}" role="img" aria-label="Commit activity chart"><polyline fill="none" stroke="#0366d6" stroke-width="3" points="${{points}}"/><line x1="${{padding}}" y1="${{height-padding}}" x2="${{width-padding}}" y2="${{height-padding}}" stroke="#d0d7de"/><text x="${{padding}}" y="${{height-8}}" font-size="11" fill="#586069">${{data[0].x}}</text><text x="${{width-padding}}" y="${{height-8}}" text-anchor="end" font-size="11" fill="#586069">${{data[data.length-1].x}}</text></svg>`;
}}
</script>
</body>
</html>"""

    return html_document


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Shivain-codes"
    print(f"Fetching stats for {username}...", file=sys.stderr)
    try:
        stats = get_user_stats(username)
        html_document = generate_html(stats)
        os.makedirs("reports", exist_ok=True)
        output_path = "reports/index.html"
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_document)
        print(f"Report generated: {output_path}", file=sys.stderr)
    except Exception as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        sys.exit(1)
