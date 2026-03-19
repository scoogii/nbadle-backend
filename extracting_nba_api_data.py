"""
Scrapes Basketball Reference for all active NBA player data.
Outputs active_players_data.csv with columns matching the expected format:
PERSON_ID, DISPLAY_FIRST_LAST, BIRTHDATE, JERSEY, TEAM_NAME, POSITION, DRAFT_NUMBER, TEAM_CONFERENCE, HEADSHOT
"""

import time
import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from nba_api.stats.static import players as nba_static_players

# Basketball Reference team abbreviations -> (team name, conference)
TEAMS = {
    "ATL": ("Hawks", "East"),
    "BOS": ("Celtics", "East"),
    "BRK": ("Nets", "East"),
    "CHO": ("Hornets", "East"),
    "CHI": ("Bulls", "East"),
    "CLE": ("Cavaliers", "East"),
    "DAL": ("Mavericks", "West"),
    "DEN": ("Nuggets", "West"),
    "DET": ("Pistons", "East"),
    "GSW": ("Warriors", "West"),
    "HOU": ("Rockets", "West"),
    "IND": ("Pacers", "East"),
    "LAC": ("Clippers", "West"),
    "LAL": ("Lakers", "West"),
    "MEM": ("Grizzlies", "West"),
    "MIA": ("Heat", "East"),
    "MIL": ("Bucks", "East"),
    "MIN": ("Timberwolves", "West"),
    "NOP": ("Pelicans", "West"),
    "NYK": ("Knicks", "East"),
    "OKC": ("Thunder", "West"),
    "ORL": ("Magic", "East"),
    "PHI": ("76ers", "East"),
    "PHO": ("Suns", "West"),
    "POR": ("Trail Blazers", "West"),
    "SAC": ("Kings", "West"),
    "SAS": ("Spurs", "West"),
    "TOR": ("Raptors", "East"),
    "UTA": ("Jazz", "West"),
    "WAS": ("Wizards", "East"),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

SEASON = 2025  # Basketball Reference uses the end year (2024-25 season = 2025)


def get_nba_headshot_map():
    """
    Build a mapping of normalized player name -> NBA.com headshot URL
    using nba_api's static (local) player data.
    """
    headshot_map = {}
    for p in nba_static_players.get_players():
        nba_id = p["id"]
        url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png"
        headshot_map[_normalize_name(p["full_name"])] = url
    return headshot_map


def _normalize_name(name):
    """Normalize a player name for fuzzy matching (strip accents, punctuation, suffixes)."""
    import unicodedata
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.lower().replace(".", "").replace("-", "").replace("'", "")
    for suffix in [" jr", " sr", " ii", " iii", " iv"]:
        name = name.removesuffix(suffix)
    return name.strip()


def get_draft_data():
    """
    Scrape draft pages for recent years to build a mapping of
    player name -> draft pick number.
    """
    draft_map = {}
    # Scrape enough years to cover all active players (roughly 20 years)
    for year in range(2000, SEASON + 1):
        url = f"https://www.basketball-reference.com/draft/NBA_{year}.html"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            tables = pd.read_html(StringIO(r.text))
            if not tables:
                continue
            draft_df = tables[0]
            # Flatten multi-level columns
            draft_df.columns = [col[-1] if isinstance(col, tuple) else col for col in draft_df.columns]
            for _, row in draft_df.iterrows():
                player = str(row.get("Player", ""))
                pick = row.get("Pk", "")
                if player and player != "Player" and str(pick).isdigit():
                    draft_map[player] = (str(int(float(pick))), str(year))
            print(f"  Scraped {year} draft ({len(draft_df)} picks)")
        except Exception as e:
            print(f"  Error scraping {year} draft: {e}")
        time.sleep(3)
    return draft_map


def get_team_roster(team_abbr, team_name, conference, headshot_map):
    """
    Scrape a team's roster page from Basketball Reference.
    Returns a list of player dicts.
    """
    url = f"https://www.basketball-reference.com/teams/{team_abbr}/{SEASON}.html"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"  Error fetching {team_abbr}: HTTP {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    roster_table = soup.find("table", {"id": "roster"})
    if not roster_table:
        print(f"  No roster table found for {team_abbr}")
        return []

    players = []
    tbody = roster_table.find("tbody")
    for row in tbody.find_all("tr"):
        cells = {
            cell.get("data-stat"): cell for cell in row.find_all(["td", "th"])
        }

        player_cell = cells.get("player")
        if not player_cell:
            continue

        player_name = player_cell.text.strip()
        # Get the bball-ref player ID from the link
        player_link = player_cell.find("a")
        bbref_id = ""
        if player_link:
            # e.g. /players/b/brownja02.html -> brownja02
            href = player_link["href"]
            bbref_id = href.split("/")[-1].replace(".html", "")

        jersey = cells.get("number", None)
        jersey = jersey.text.strip() if jersey else ""
        if "," in jersey:
            jersey = jersey.split(",")[0].strip()

        pos = cells.get("pos", None)
        pos = pos.text.strip() if pos else ""

        birth_date = cells.get("birth_date", None)
        birth_date = birth_date.text.strip() if birth_date else ""

        # Map position abbreviations to match existing format
        pos_map = {"PG": "Guard", "SG": "Guard", "SF": "Forward", "PF": "Forward", "C": "Center"}
        position = pos_map.get(pos, pos)

        headshot = headshot_map.get(
            _normalize_name(player_name),
            f"https://cdn.nba.com/headshots/nba/latest/1040x760/fallback.png",
        )

        players.append({
            "PERSON_ID": bbref_id,
            "DISPLAY_FIRST_LAST": player_name,
            "BIRTHDATE": birth_date,
            "JERSEY": jersey,
            "TEAM_NAME": team_name,
            "POSITION": position,
            "DRAFT_NUMBER": "",  # Filled in later
            "DRAFT_YEAR": "",  # Filled in later
            "TEAM_CONFERENCE": conference,
            "HEADSHOT": headshot,
        })

    return players


def create_csv():
    print("Loading NBA headshot data...")
    headshot_map = get_nba_headshot_map()
    print(f"Loaded {len(headshot_map)} player headshot URLs\n")

    print("Scraping draft data...")
    draft_map = get_draft_data()
    print(f"Collected draft data for {len(draft_map)} players\n")

    print("Scraping team rosters...")
    all_players = []
    for team_abbr, (team_name, conference) in TEAMS.items():
        print(f"  {team_name} ({team_abbr})...")
        players = get_team_roster(team_abbr, team_name, conference, headshot_map)
        all_players.extend(players)
        time.sleep(3)  # Be respectful of rate limits

    # Fill in draft numbers and draft years
    for player in all_players:
        name = player["DISPLAY_FIRST_LAST"]
        draft_info = draft_map.get(name)
        if draft_info:
            player["DRAFT_NUMBER"] = draft_info[0]
            player["DRAFT_YEAR"] = draft_info[1]
        else:
            player["DRAFT_NUMBER"] = "Undrafted"
            player["DRAFT_YEAR"] = "Undrafted"

    df = pd.DataFrame(all_players)
    # Remove duplicates from players on multiple rosters (e.g. mid-season trades)
    # Keep the last occurrence (later teams in the loop are typically the traded-to team)
    df = df.drop_duplicates(subset="DISPLAY_FIRST_LAST", keep="last")
    print(f"\nTotal players: {len(df)}")
    df.to_csv("active_players_data.csv", index=False, encoding="utf-8")
    print("Saved to active_players_data.csv")


if __name__ == "__main__":
    create_csv()
