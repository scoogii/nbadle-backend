"""
Scrapes Basketball Reference for the top 200 players by points per game.
Outputs top_200_players_id.csv with PLAYER_ID column (bball-ref player IDs).
"""

import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

SEASON = 2025


def create_top_players_csv():
    url = f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_per_game.html"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", {"id": "per_game_stats"})
    tbody = table.find("tbody")

    # Collect player IDs and their PTS for sorting
    seen = set()
    players = []
    for row in tbody.find_all("tr"):
        if row.get("class") and "thead" in row.get("class"):
            continue
        player_cell = row.find("td", {"data-stat": "name_display"})
        pts_cell = row.find("td", {"data-stat": "pts_per_g"})
        if not player_cell or not pts_cell:
            continue

        player_link = player_cell.find("a")
        if not player_link:
            continue

        # e.g. /players/g/gilMDsh01.html -> gilMDsh01
        href = player_link["href"]
        bbref_id = href.split("/")[-1].replace(".html", "")

        # Skip duplicate entries (players traded mid-season appear multiple times)
        if bbref_id in seen:
            continue
        seen.add(bbref_id)

        try:
            pts = float(pts_cell.text)
        except (ValueError, TypeError):
            continue

        players.append({"PLAYER_ID": bbref_id, "PTS": pts})

    # Sort by points descending and take top 200
    players_df = pd.DataFrame(players)
    players_df = players_df.sort_values("PTS", ascending=False).head(200)

    top_200_df = players_df[["PLAYER_ID"]]
    print(f"Top 200 players by PPG:")
    print(top_200_df.head(10).to_string(index=False))
    top_200_df.to_csv("top_200_players_id.csv", index=False, encoding="utf-8")
    print(f"\nSaved {len(top_200_df)} players to top_200_players_id.csv")


if __name__ == "__main__":
    create_top_players_csv()
