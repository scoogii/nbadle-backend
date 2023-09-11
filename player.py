import random
import numpy
import pandas as pd

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


def get_player():
    # TODO: Make CSV for this too
    # Get top 100 players in the NBA

    # Create players dataframe from csv
    players_df = pd.read_csv("./player_data.csv")

    # Choose a random player ID from active players
    player_id = random.choice(players_df["PERSON_ID"].tolist())

    # Find row corresponding to player_id
    player_row = players_df.loc[players_df["PERSON_ID"] == numpy.int64(player_id)]

    playerStats = {
        "full_name": player_row["DISPLAY_FIRST_LAST"].iloc[0],
        "headshot": player_row["HEADSHOT"].iloc[0],
        "team_name": player_row["TEAM_NAME"].iloc[0],
        "conference": player_row["TEAM_CONFERENCE"].iloc[0],
        "age": int(player_row["Age"].iloc[0]),
        "position": player_row["POSITION"].iloc[0],
        "player_number": int(player_row["JERSEY"].iloc[0]),
        "draft_number": player_row["DRAFT_NUMBER"].iloc[0],
    }

    return playerStats


def get_names():
    # Get top 100 players in the NBA
    players_df = pd.read_csv("./player_data.csv")
    player_names = players_df["DISPLAY_FIRST_LAST"].tolist()

    return player_names


def get_player_by_full_name(player_full_name):
    players_df = pd.read_csv("./player_data.csv")

    # Find row corresponding to player_id
    player_row = players_df.loc[players_df["DISPLAY_FIRST_LAST"] == player_full_name]
    print(player_row)

    playerStats = {
        "full_name": player_full_name,
        "headshot": player_row["HEADSHOT"].iloc[0],
        "team_name": player_row["TEAM_NAME"].iloc[0],
        "conference": player_row["TEAM_CONFERENCE"].iloc[0],
        "age": int(player_row["Age"].iloc[0]),
        "position": player_row["POSITION"].iloc[0],
        "player_number": int(player_row["JERSEY"].iloc[0]),
        "draft_number": player_row["DRAFT_NUMBER"].iloc[0],
    }

    return playerStats


if __name__ == "__main__":
    print(get_player_by_full_name("LeBron James"))
