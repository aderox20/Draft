#!/usr/bin/env python3
import json
import os
import urllib.request
from collections import Counter

USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "aderox20")
OUT = "profile"
os.makedirs(OUT, exist_ok=True)

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "aderox20-profile-stats"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

user = get_json(f"https://api.github.com/users/{USER}")
repos = []
page = 1
while page <= 10:
    batch = get_json(f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}")
    if not batch:
        break
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1

stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
languages = Counter()

for repo in repos:
    if repo.get("fork"):
        continue
    try:
        data = get_json(repo["languages_url"])
        for lang, count in data.items():
            languages[lang] += count
    except Exception:
        pass

top_langs = languages.most_common(6)
total_bytes = sum(languages.values()) or 1

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def card(title, rows, filename, width=495, height=245):
    y = 58
    body = []
    for label, value in rows:
        body.append(
            f'<text x="28" y="{y}" fill="#c9d1d9" font-size="16" font-family="Arial,sans-serif">{esc(label)}</text>'
            f'<text x="{width-28}" y="{y}" text-anchor="end" fill="#f0f6fc" font-size="18" font-weight="700" font-family="Arial,sans-serif">{esc(value)}</text>'
        )
        y += 35
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="28" y="34" fill="#f0f6fc" font-size="20" font-weight="700" font-family="Arial,sans-serif">{esc(title)}</text>
{"".join(body)}
</svg>
'''
    with open(os.path.join(OUT, filename), "w", encoding="utf-8") as f:
        f.write(svg)

card(
    f"{USER}'s GitHub Stats",
    [
        ("Public repositories", user.get("public_repos", 0)),
        ("Followers", user.get("followers", 0)),
        ("Following", user.get("following", 0)),
        ("Stars earned", stars),
        ("Forks", forks),
    ],
    "stats.svg",
)
# .
rows = [(lang, f"{count / total_bytes * 100:.1f}%") for lang, count in top_langs]
card(f"{USER}'s Top Languages", rows or [("No language data", "—")], "languages.svg", height=max(120, 65 + len(rows) * 35))
