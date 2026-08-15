import html
import os
import sys

from fetch_github import get_user_stats


def generate_html(stats):
    total_repos = sum(stats["languages"].values()) or 1
    palette = ["#4F86F7", "#1D9E75", "#E24B4A", "#EF9F27", "#7F77DD", "#D85A30"]
    lang_html = "".join(
        f'''<div class="lang-row"><span class="lang-name">{html.escape(lang)}</span><div class="lang-track"><div class="lang-fill" style="width:{round(count / total_repos * 100)}%;background:{palette[i % len(palette)]}"></div></div><span class="muted">{round(count / total_repos * 100)}%</span></div>'''
        for i, (lang, count) in enumerate(stats["languages"].items())
    ) or '<p class="muted">No language data available.</p>'

    active_repos = "".join(
        f'<li><strong>{html.escape(repo)}</strong><span>{count} {"commit" if count == 1 else "commits"}</span></li>'
        for repo, count in stats["commit_repos"].items()
    ) or '<li><span class="muted">No recent commit activity detected</span></li>'

    top_repos = "".join(
        f'''<article class="repo"><div class="repo-title">{html.escape(repo["name"])}</div><div class="repo-desc">{html.escape(repo["description"] or "No description")}</div><div class="repo-meta"><span>{html.escape(repo["language"])}</span><span>★ {repo["stars"]}</span><span>Forks {repo["forks"]}</span></div></article>'''
        for repo in stats["top_repos"]
    ) or '<p class="muted">No repositories found.</p>'

    daily_data = ",".join(
        f"{{d:'{day}',v:{count}}}" for day, count in stats["daily_commits"].items()
    )
    username = html.escape(stats["username"])
    name = html.escape(stats["name"] or username)
    bio = html.escape(stats["bio"] or "GitHub developer")
    generated_at = html.escape(stats["generated_at"])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="GitTrack developer analytics for @{username}">
<title>GitTrack — @{username}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0d1117;color:#e6edf3;padding:28px}}
.container{{max-width:1080px;margin:auto}}.hero{{padding:30px;border:1px solid #30363d;border-radius:16px;background:linear-gradient(135deg,#161b22,#0d1117);margin-bottom:18px}}
.eyebrow{{color:#58a6ff;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px}}h1{{font-size:32px}}.handle{{color:#8b949e;margin-top:4px}}.bio{{color:#8b949e;margin-top:12px;max-width:700px;line-height:1.5}}.updated{{color:#6e7681;font-size:12px;margin-top:16px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}}.card,.section{{background:#161b22;border:1px solid #30363d;border-radius:12px}}.card{{padding:18px}}.number{{font-size:28px;font-weight:700}}.label{{font-size:12px;color:#8b949e;margin-top:5px}}
.section{{padding:20px;margin-bottom:18px}}h2{{font-size:16px;margin-bottom:16px}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.metric{{background:#0d1117;border:1px solid #21262d;border-radius:9px;padding:15px}}.metric strong{{display:block;font-size:18px;margin-bottom:5px}}.muted{{color:#8b949e;font-size:12px}}
.chart{{height:240px;width:100%;overflow:hidden}}.lang-row{{display:flex;align-items:center;gap:10px;margin:11px 0}.lang-name{{width:100px;font-size:13px}.lang-track{{height:8px;flex:1;background:#21262d;border-radius:20px;overflow:hidden}.lang-fill{{height:100%;border-radius:20px}}
ul{{list-style:none}}.active-list li{{display:flex;justify-content:space-between;padding:11px 0;border-bottom:1px solid #21262d;font-size:13px}}.active-list li:last-child{{border:0}}
.repo{{border:1px solid #30363d;border-radius:9px;padding:15px;margin-top:10px}}.repo-title{{font-weight:700;color:#58a6ff}}.repo-desc{{font-size:13px;color:#8b949e;margin:6px 0;line-height:1.4}}.repo-meta{{display:flex;gap:18px;color:#8b949e;font-size:12px}}
.footer{{text-align:center;color:#6e7681;font-size:11px;padding:10px}}@media(max-width:720px){{body{{padding:14px}}.grid,.metrics{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:26px}}}}
</style></head>
<body><main class="container">
<header class="hero"><div class="eyebrow">GitTrack • Developer Analytics</div><h1>{name}</h1><div class="handle">@{username}</div><p class="bio">{bio}</p><p class="updated">Updated {generated_at}</p></header>
<section class="grid"><div class="card"><div class="number">{stats["weekly_commits"]}</div><div class="label">Commits · 7 days</div></div><div class="card"><div class="number">{stats["monthly_commits"]}</div><div class="label">Commits · 30 days</div></div><div class="card"><div class="number">{stats["current_streak"]}</div><div class="label">Current streak</div></div><div class="card"><div class="number">{stats["public_repos"]}</div><div class="label">Public repositories</div></div></section>
<section class="section"><h2>Developer snapshot</h2><div class="metrics"><div class="metric"><strong>{stats["longest_streak"]} days</strong><span class="muted">Longest tracked streak</span></div><div class="metric"><strong>{html.escape(stats["most_active_repo"])}</strong><span class="muted">Most active repository</span></div><div class="metric"><strong>{stats["average_commits_per_week"]}</strong><span class="muted">Average commits / week</span></div><div class="metric"><strong>{html.escape(stats["most_productive_day"])}</strong><span class="muted">Most productive day</span></div></div></section>
<section class="section"><h2>Commit activity · 90 days</h2><div id="chart" class="chart"></div><p class="muted">Public GitHub events available to GitTrack; GitHub may limit how far public event history can be queried.</p></section>
<section class="section"><h2>Languages across repositories</h2>{lang_html}</section>
<section class="section"><h2>Most active repositories</h2><ul class="active-list">{active_repos}</ul></section>
<section class="section"><h2>Top repositories by stars</h2>{top_repos}</section>
<footer class="footer">GitTrack · Automated developer analytics · Generated by GitHub Actions</footer>
</main>
<script>
const data=[{daily_data}],el=document.getElementById('chart');
if(!data.length){{el.innerHTML='<p class="muted">No commit activity available.</p>';}}else{{const w=el.clientWidth||900,h=220,p=32,max=Math.max(...data.map(x=>x.v),1),x=i=>p+i*(w-p*2)/Math.max(data.length-1,1),y=v=>h-p-v/max*(h-p*2),pts=data.map((d,i)=>`${{x(i)}},${{y(d.v)}}`).join(' ');el.innerHTML=`<svg width="100%" height="220" viewBox="0 0 ${{w}} ${{h}}"><polyline fill="none" stroke="#58a6ff" stroke-width="3" points="${{pts}}"/><line x1="${{p}}" y1="${{h-p}}" x2="${{w-p}}" y2="${{h-p}}" stroke="#30363d"/><text x="${{p}}" y="${{h-8}}" fill="#8b949e" font-size="11">${{data[0].d}}</text><text x="${{w-p}}" y="${{h-8}}" text-anchor="end" fill="#8b949e" font-size="11">${{data[data.length-1].d}}</text></svg>`;}}
</script></body></html>'''


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Shivain-codes"
    print(f"Fetching stats for {username}...", file=sys.stderr)
    try:
        stats = get_user_stats(username)
        os.makedirs("reports", exist_ok=True)
        with open("reports/index.html", "w", encoding="utf-8") as file:
            file.write(generate_html(stats))
        print("Report generated: reports/index.html", file=sys.stderr)
    except Exception as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        sys.exit(1)
