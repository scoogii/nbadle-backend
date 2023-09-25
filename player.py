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
    top_100 = pd.read_csv("./top_100_players_id.csv")

    # Choose a random player ID from active players
    player_id = random.choice(top_100["PLAYER_ID"].tolist())

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
    stored_time_read = open("time.txt", "r")
    stored_player_read = open("player.txt", "r")
    stored_time_value = stored_time_read.readline().strip()
    stored_player_value = stored_player_read.readline().strip()
    stored_time_read.close()
    stored_player_read.close()

    # If the current date equals stored date, return stored player data
    if date.today() == datetime.strptime(stored_time_value, "%Y-%m-%d").date():
        return get_player_by_full_name(stored_player_value)
    # If the current date is greater than the stored date
    elif date.today() > datetime.strptime(stored_time_value, "%Y-%m-%d").date():
        # Get a new player from top_100_players_id.csv and get their data
        new_player = get_player()
        if new_player["full_name"] == stored_player_value:
            new_player = get_player()
        # Change time.txt to the new current time
        stored_time_write = open("time.txt", "w")
        stored_time_write.write(str(date.today()))
        stored_time_write.close()
        # Change player.txt to the new player's name
        stored_player_write = open("player.txt", "w")
        stored_player_write.write(new_player["full_name"])
        stored_player_write.close()
        # Return the player's data
        return new_player


if __name__ == "__main__":
    print(get_daily_player())
