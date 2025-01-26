from webbrowser import get
import requests
import csv
import time
import nba_api
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo, teaminfocommon, commonallplayers
from nba_api.stats.static import players


def crawl(a):

    global run
    run = run + 1

    # Create x, y

    df2 = pd.DataFrame([[x, y]], columns=["X", "Y"])

    if run == 1:
        df2.to_csv("output.csv")
    if run != 1:
        df2.to_csv("output.csv", header=None, mode="a")

    df1["Column A"].apply(crawl)


def create_csv():

    # Get player id's of all active players
    # nba_players = players.get_players()
    all_players = commonallplayers.CommonAllPlayers(
        is_only_current_season=1
    ).get_dict()["resultSets"][0]["rowSet"]

    # List all players containing their player information
    player_data = []
    for active_player in all_players:
        player_info = get_player_data(active_player[0])
        time.sleep(0.6)
        player_data.append(player_info)

    final_df = pd.concat(player_data, ignore_index=True)
    final_df.to_csv("active_players_data.csv", index=False, encoding="utf-8")

    return


def get_player_data(nba_player_id):

    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-token": "true",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "x-nba-stats-origin": "stats",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://stats.nba.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }
    player_data = commonplayerinfo.CommonPlayerInfo(
        player_id=nba_player_id, headers=headers, timeout=100
    )
    player_info_dict = player_data.get_dict()
    team_id = player_info_dict["resultSets"][0]["rowSet"][0][18]

    if team_id == "":
        return

    team_data = teaminfocommon.TeamInfoCommon(
        team_id=team_id, headers=headers, timeout=100
    )
    team_df = team_data.team_info_common.get_data_frame()
    conference_df = team_df.loc[:, ["TEAM_CONFERENCE"]]

    player_info_df = player_data.common_player_info.get_data_frame()
    player_info_df = player_info_df.loc[
        :,
        [
            "PERSON_ID",
            "DISPLAY_FIRST_LAST",
            "BIRTHDATE",
            "JERSEY",
            "TEAM_NAME",
            "POSITION",
            "DRAFT_NUMBER",
        ],
    ]

    df = player_info_df.join(conference_df)
    df["HEADSHOT"] = [
        f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{nba_player_id}.png"
    ]
    print(df.iloc[0]["DISPLAY_FIRST_LAST"])
    return df


if __name__ == "__main__":
    create_csv()
