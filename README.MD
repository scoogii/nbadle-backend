# How to Update

- Run `extracting_nba_api_data.py` and `extracting_top_players_data.py`
- Open Excel and edit `active_players_data.csv` and `top_200_players_id.csv`

## For `active_players_data.csv`

- Change date format to MM/DD/YYYY
- Use `INT(YEARFRAC("CELL" - TODAY()))`
- Remove all players with no team
- Sort by names alphabetically
