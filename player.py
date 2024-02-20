import random
import numpy
import pandas as pd
from datetime import date, datetime

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
    # Get top 100 players in the NBA
    # Create players dataframe from csv
    top_players = pd.read_csv("./top_players.csv")
    # Choose a random player ID from active players
    player_id = random.choice(top_players["PLAYER_ID"].tolist())

    # Find row corresponding to player_id in stats csv
    players_df = pd.read_csv("./player_data.csv")
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


def get_daily_player():
    # Check the current date against the stored date in time.txt
    daily_df = pd.read_csv("./daily.csv")
    stored_time_value = daily_df["TIME"].iloc[0]
    stored_player_value = str(daily_df["PLAYER"].iloc[0])

    # If the current date equals stored date, return stored player data
    if date.today() == datetime.strptime(stored_time_value, "%Y-%m-%d").date():
        return get_player_by_full_name(stored_player_value)
    # If the current date is greater than the stored date
    elif date.today() > datetime.strptime(stored_time_value, "%Y-%m-%d").date():
        # Get a new player from top_players.csv and get their data
        new_player = get_player()
        if new_player["full_name"] == stored_player_value:
            new_player = get_player()

        # Change time in csv to the new current time
        daily_df.at[0, "TIME"] = str(date.today())

        # Change player in csv to the new player's name
        daily_df.at[0, "PLAYER"] = new_player["full_name"]

        daily_df.to_csv("./daily.csv", index=False)

        # Return the player's data
        return new_player


if __name__ == "__main__":
    print(get_player())
