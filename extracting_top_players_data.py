from nba_api.stats.endpoints import leagueleaders
import pandas as pd


def create_top_players_csv():
    top_200_df = pd.DataFrame()
    all_players_data = leagueleaders.LeagueLeaders()
    all_players = all_players_data.league_leaders.get_dict()["data"]
    all_players_df = pd.DataFrame(all_players)
    top_200_player_id_df = all_players_df.loc[:, 0]
    top_200_df["PLAYER_ID"] = top_200_player_id_df.head(200)
    print(top_200_player_id_df)
    top_200_df.to_csv("top_200_players_id.csv", index=False, encoding="utf-8")
    return


if __name__ == "__main__":
    create_top_players_csv()
