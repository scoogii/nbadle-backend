"""
To use after running `extracting_nba_api_data.py`

Formats:
- Removes all players where team cell is empty
- Date to DD/MM/YYYY
- Adds a column on the right for age (int)
- Changes jersey numbers to int
- Sorts csv by names alphabetically
"""

import pandas as pd
import numpy as np


def format_player_data():
    df = pd.read_csv("active_players_data.csv")

    # Remove first redundant column
    df.drop(df.columns[0], axis=1, inplace=True)

    # Remove all players with no team
    df = df.dropna()

    # Change date field to DD/MM/YYYY
    df["BIRTHDATE"] = pd.to_datetime(df["BIRTHDATE"], dayfirst=True)
    df["BIRTHDATE"] = df["BIRTHDATE"].dt.strftime("%d/%m/%Y")

    # Add age column
    if "AGE" not in df.columns:
        df.insert(3, "AGE", value="")
        df["AGE"] = (
            np.floor(
                (
                    pd.to_datetime("today")
                    - pd.to_datetime(df["BIRTHDATE"], dayfirst=True)
                ).dt.days
                / 365.25
            )
        ).astype(int)

    # Change jersey number to int
    df["JERSEY"] = pd.to_numeric(df["JERSEY"], downcast="integer")

    # Sort by first name
    df = df.sort_values(by=["DISPLAY_FIRST_LAST"], ascending=True)

    return df


if __name__ == "__main__":
    df = format_player_data()
    print(df)
    df.to_csv("active_players_data.csv", index=False)
