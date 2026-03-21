"""
Fetches WNBA player data using nba_api.
Outputs wnba_player_data.csv and wnba_top_players.csv with columns matching
the NBA format:
PERSON_ID, DISPLAY_FIRST_LAST, BIRTHDATE, AGE, JERSEY, TEAM_NAME, POSITION,
DRAFT_NUMBER, DRAFT_YEAR, TEAM_CONFERENCE, HEADSHOT
"""

import re
import time
import unicodedata
import pandas as pd
from datetime import date
from nba_api.stats.static import teams as static_teams
from nba_api.stats.endpoints import (
    CommonTeamRoster,
    LeagueStandingsV3,
    commonplayerinfo,
)

SEASON = "2025"
HEADSHOT_BASE = "https://cdn.wnba.com/headshots/wnba/latest/1040x760"
REQUEST_DELAY = 0.6


def normalize_name(name):
    """
    Normalize accented/unicode characters to clean ASCII.
    e.g. Dončić -> Doncic, Fágbénlé -> Fagbenle
    """
    # NFD decomposes characters, then we strip combining marks
    decomposed = unicodedata.normalize("NFD", name)
    stripped = re.sub(r"[\u0300-\u036f]", "", decomposed)
    # Encode to ASCII to catch any remaining non-ASCII, replacing with closest match
    return stripped.encode("ascii", "ignore").decode("ascii")


def get_conference_map():
    """Get team_id -> conference mapping from standings."""
    try:
        standings = LeagueStandingsV3(
            league_id="10", season=SEASON, season_type="Regular Season"
        )
        df = standings.get_data_frames()[0]
        return dict(zip(df["TeamID"], df["Conference"]))
    except Exception as e:
        print(f"Warning: Could not fetch standings ({e}), using fallback conference map")
        # Fallback based on 2024 season
        return {
            1611661313: "East",  # Liberty
            1611661317: "West",  # Mercury
            1611661319: "West",  # Aces
            1611661320: "West",  # Sparks
            1611661321: "West",  # Wings
            1611661322: "East",  # Mystics
            1611661323: "East",  # Sun
            1611661324: "West",  # Lynx
            1611661325: "East",  # Fever
            1611661328: "West",  # Storm
            1611661329: "East",  # Sky
            1611661330: "East",  # Dream
            1611661331: "West",  # Valkyries
        }


def get_rosters(conf_map):
    """Get all WNBA team rosters via CommonTeamRoster."""
    wnba_teams = static_teams.get_wnba_teams()
    all_players = []

    for team in wnba_teams:
        team_id = team["id"]
        team_name = team["nickname"]
        conference = conf_map.get(team_id, "")
        print(f"  {team_name}...", end=" ")

        try:
            roster = CommonTeamRoster(
                team_id=team_id, league_id_nullable="10", season=SEASON
            )
            df = roster.common_team_roster.get_data_frame()
        except Exception as e:
            print(f"ERROR ({e})")
            time.sleep(REQUEST_DELAY)
            continue

        for _, row in df.iterrows():
            all_players.append(
                {
                    "PLAYER_ID": row["PLAYER_ID"],
                    "DISPLAY_FIRST_LAST": normalize_name(str(row["PLAYER"])),
                    "TEAM_NAME": team_name,
                    "TEAM_ID": team_id,
                    "TEAM_CONFERENCE": conference,
                }
            )

        print(f"{len(df)} players")
        time.sleep(REQUEST_DELAY)

    return all_players


def enrich_with_player_info(players):
    """Fetch draft info, position, jersey, birthdate, age from CommonPlayerInfo."""
    enriched = []
    total = len(players)

    for i, player in enumerate(players):
        pid = player["PLAYER_ID"]
        name = player["DISPLAY_FIRST_LAST"]
        print(f"  [{i + 1}/{total}] {name}...", end=" ")

        try:
            info = commonplayerinfo.CommonPlayerInfo(
                player_id=pid, league_id_nullable="10", timeout=15
            )
            df = info.common_player_info.get_data_frame()
            row = df.iloc[0]

            draft_number = str(row.get("DRAFT_NUMBER", "Undrafted"))
            draft_year = str(row.get("DRAFT_YEAR", "Undrafted"))
            if not draft_number or draft_number == "0":
                draft_number = "Undrafted"
                draft_year = "Undrafted"

            position = str(row.get("POSITION", ""))
            jersey = str(row.get("JERSEY", ""))
            birthdate_raw = str(row.get("BIRTHDATE", ""))

            # Calculate age from birthdate
            age = 0
            if birthdate_raw and birthdate_raw != "None":
                try:
                    bd = pd.to_datetime(birthdate_raw).date()
                    today = date.today()
                    age = (
                        today.year
                        - bd.year
                        - ((today.month, today.day) < (bd.month, bd.day))
                    )
                    birthdate_raw = bd.strftime("%d/%m/%Y")
                except Exception:
                    pass

            player_data = {
                "PERSON_ID": pid,
                "DISPLAY_FIRST_LAST": name,
                "BIRTHDATE": birthdate_raw,
                "AGE": age,
                "JERSEY": jersey if jersey and jersey != "None" else "0",
                "TEAM_NAME": player["TEAM_NAME"],
                "POSITION": position if position else "Forward",
                "DRAFT_NUMBER": draft_number,
                "DRAFT_YEAR": draft_year,
                "TEAM_CONFERENCE": player["TEAM_CONFERENCE"],
                "HEADSHOT": f"{HEADSHOT_BASE}/{pid}.png",
            }

            enriched.append(player_data)
            print("OK")

        except Exception as e:
            print(f"ERROR ({e}), using defaults")
            # Still include player with available data
            enriched.append(
                {
                    "PERSON_ID": pid,
                    "DISPLAY_FIRST_LAST": name,
                    "BIRTHDATE": "",
                    "AGE": 0,
                    "JERSEY": "0",
                    "TEAM_NAME": player["TEAM_NAME"],
                    "POSITION": "Forward",
                    "DRAFT_NUMBER": "Undrafted",
                    "DRAFT_YEAR": "Undrafted",
                    "TEAM_CONFERENCE": player["TEAM_CONFERENCE"],
                    "HEADSHOT": f"{HEADSHOT_BASE}/{pid}.png",
                }
            )

        time.sleep(REQUEST_DELAY)

    return enriched


def validate_data(df):
    """Check for missing or invalid data and report issues."""
    issues = []
    for col in df.columns:
        nulls = df[col].isna().sum()
        if nulls > 0:
            issues.append(f"  {col}: {nulls} null values")
        empties = (df[col].astype(str) == "").sum()
        if empties > 0:
            issues.append(f"  {col}: {empties} empty strings")

    if issues:
        print("\nData quality warnings:")
        for issue in issues:
            print(issue)
    else:
        print("\nData quality: all fields populated ✓")


def create_csv():
    print("Fetching WNBA conference data...")
    conf_map = get_conference_map()
    print(f"Got conferences for {len(conf_map)} teams\n")

    print("Fetching WNBA rosters...")
    players = get_rosters(conf_map)
    print(f"\nTotal rostered players: {len(players)}\n")

    if not players:
        print("ERROR: No players found. Aborting.")
        return

    print("Fetching player details (draft, position, jersey, age)...")
    enriched = enrich_with_player_info(players)

    df = pd.DataFrame(enriched)
    # Remove duplicates (players traded mid-season)
    df = df.drop_duplicates(subset="PERSON_ID", keep="last")

    validate_data(df)

    # Save full player data
    df.to_csv("wnba_player_data.csv", index=False, encoding="utf-8")
    print(f"\nSaved wnba_player_data.csv ({len(df)} players)")

    # Save top players list (all rostered WNBA players)
    top_df = df[["PERSON_ID"]].rename(columns={"PERSON_ID": "PLAYER_ID"})
    top_df.to_csv("wnba_top_players.csv", index=False, encoding="utf-8")
    print(f"Saved wnba_top_players.csv ({len(top_df)} players)")


if __name__ == "__main__":
    create_csv()
