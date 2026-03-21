import random
import unicodedata
import pandas as pd
from datetime import date, datetime


def _normalize_display_name(name):
    """Normalize accented characters to ASCII (e.g. Dončić -> Doncic)."""
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")

headers = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.nba.com/",
    "Origin": "stats.nba.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}


def _get_player_stats(player_row):
    """Extract player stats dict from a DataFrame row."""
    return {
        "full_name": player_row["DISPLAY_FIRST_LAST"].iloc[0],
        "headshot": player_row["HEADSHOT"].iloc[0],
        "team_name": player_row["TEAM_NAME"].iloc[0],
        "conference": player_row["TEAM_CONFERENCE"].iloc[0],
        "age": int(player_row["AGE"].iloc[0]),
        "position": player_row["POSITION"].iloc[0],
        "player_number": int(player_row["JERSEY"].iloc[0]),
        "draft_number": player_row["DRAFT_NUMBER"].iloc[0],
        "draft_year": player_row["DRAFT_YEAR"].iloc[0],
    }


def _read_players(csv_path="./player_data.csv"):
    """Read a player CSV with normalized display names."""
    df = pd.read_csv(csv_path)
    df["DISPLAY_FIRST_LAST"] = df["DISPLAY_FIRST_LAST"].apply(_normalize_display_name)
    return df


def _get_random_player(top_csv, data_csv):
    """Pick a random player from a top-players CSV and return their stats."""
    top_players = pd.read_csv(top_csv)
    player_id = random.choice(top_players["PLAYER_ID"].tolist())
    players_df = _read_players(data_csv)
    player_row = players_df.loc[players_df["PERSON_ID"] == player_id]
    return _get_player_stats(player_row)


def _get_player_by_name(player_full_name, data_csv):
    """Look up a player by name from a given CSV."""
    players_df = _read_players(data_csv)
    player_row = players_df.loc[players_df["DISPLAY_FIRST_LAST"] == player_full_name]
    if player_row.empty:
        return None
    return _get_player_stats(player_row)


def _get_daily(daily_csv, top_csv, data_csv, get_random_fn, get_by_name_fn):
    """Generic daily player logic for any league."""
    daily_df = pd.read_csv(daily_csv)
    stored_time_value = daily_df["TIME"].iloc[0]
    stored_player_value = str(daily_df["PLAYER"].iloc[0])

    stored_date = datetime.strptime(stored_time_value, "%Y-%m-%d").date()
    if date.today() <= stored_date:
        return get_by_name_fn(stored_player_value)
    else:
        new_player = get_random_fn()
        if new_player["full_name"] == stored_player_value:
            new_player = get_random_fn()

        daily_df.at[0, "TIME"] = str(date.today())
        daily_df.at[0, "PLAYER"] = new_player["full_name"]
        daily_df.to_csv(daily_csv, index=False)

        return new_player


# --- NBA ---

def get_player():
    return _get_random_player("./top_players.csv", "./player_data.csv")


def get_names():
    players_df = _read_players("./player_data.csv")
    return players_df["DISPLAY_FIRST_LAST"].tolist()


def get_player_by_full_name(player_full_name):
    return _get_player_by_name(player_full_name, "./player_data.csv")


def get_daily_player():
    return _get_daily(
        "./daily.csv", "./top_players.csv", "./player_data.csv",
        get_player, get_player_by_full_name,
    )


# --- WNBA ---

def get_wnba_player():
    return _get_random_player("./wnba_top_players.csv", "./wnba_player_data.csv")


def get_wnba_names():
    players_df = _read_players("./wnba_player_data.csv")
    return sorted(players_df["DISPLAY_FIRST_LAST"].tolist())


def get_wnba_player_by_full_name(player_full_name):
    return _get_player_by_name(player_full_name, "./wnba_player_data.csv")


def get_wnba_daily_player():
    return _get_daily(
        "./wnba_daily.csv", "./wnba_top_players.csv", "./wnba_player_data.csv",
        get_wnba_player, get_wnba_player_by_full_name,
    )


if __name__ == "__main__":
    print(get_player())
