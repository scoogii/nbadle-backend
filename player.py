import random
from nba_api.stats.static import players
from nba_api.stats.endpoints import (
    commonplayerinfo,
    leagueleaders,
    teaminfocommon,
    draftboard,
)
from datetime import datetime

headers = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "stats.nba.com",
    "Origin": "stats.nba.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}


def getAge(birth_date):
    date_format = "%Y-%m-%d"
    today = datetime.now()
    birth_date = datetime.strptime(birth_date[0:10], date_format)

    age = today - birth_date

    return age.days // 365


def get_player():
    # Get top 100 players in the NBA
    # top_100 = leagueleaders.LeagueLeaders(headers=headers).get_dict()["resultSet"][
    #     "rowSet"
    # ][:100]
    #
    # player = top_100[0]
    # player_id = player[0]
    # team_name = player[4]

    hi = draftboard.DraftBoard().get_dict()
    return {
        "hi": hi,
    }

    # return {
    #     "id": player_id,
    #     "full_name": player[2],
    #     "headshot": f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png",
    #     "team_name": team_name,
    #     "yo": hi,
    # }
    # Choose a random player ID from active players
    # player = random.choice(top_100)
    # player_id = player[0]

    # Retrieve player position, jersey number, and draft number
    # player_info_dict = commonplayerinfo.CommonPlayerInfo(
    #     player_id, headers=headers
    # ).get_dict()

    # player_info = player_info_dict["resultSets"][0]["rowSet"][0]

    # team_id = player_info[18]
    # player_position = player_info[15]
    # player_no = player_info[14]
    # draft_pick = "Undrafted" if player_info[-2] == "Undrafted" else player_info[-2]
    # conference = teaminfocommon.TeamInfoCommon(team_id, headers=headers).get_dict()[
    #     "resultSets"
    # ][0]["rowSet"][0][5]
    #
    # playerStats = {
    #     "full_name": player_info[3],
    #     "headshot": f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png",
    #     "team_name": player_info[20],
    #     "conference": conference,
    #     "age": getAge(player_info[7]),
    #     "position": player_position,
    #     "player_number": player_no,
    #     "draft_number": draft_pick,
    # }

    # return playerStats


def get_names():
    # Get top 100 players in the NBA
    all_players = players.get_active_players()

    player_names = sorted([player["full_name"] for player in all_players])

    return player_names


def get_player_by_full_name(player_full_name):
    player_id = players.find_players_by_full_name(player_full_name)[0]["id"]

    # Retrieve player position, jersey number, and draft number
    player_info_dict = commonplayerinfo.CommonPlayerInfo(player_id).get_dict()
    player_info = player_info_dict["resultSets"][0]["rowSet"][0]

    team_id = player_info[18]
    player_position = player_info[15]
    player_no = player_info[14]
    draft_pick = "Undrafted" if player_info[-2] == "Undrafted" else player_info[-2]
    conference = teaminfocommon.TeamInfoCommon(team_id).get_dict()["resultSets"][0][
        "rowSet"
    ]
    conference = conference[0][5] if conference else "N/A"

    playerStats = {
        "headshot": f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png",
        "team_name": player_info[20],
        "conference": conference,
        "age": getAge(player_info[7]),
        "position": player_position,
        "player_number": player_no,
        "draft_number": draft_pick,
    }

    return playerStats


if __name__ == "__main__":
    pass
