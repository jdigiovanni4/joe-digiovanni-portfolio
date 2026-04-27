import pandas as pd
import time
import warnings
from pybaseball import team_batting, schedule_and_record
import os

warnings.simplefilter(action='ignore', category=FutureWarning)

def fetch_season_aggregates(start_year, end_year):
    print(f"Fetching season aggregates ({start_year}-{end_year})...")
    data = pd.DataFrame()
    
    for year in range(start_year, end_year + 1):
        try:
            print(f"  Downloading {year}...")
            yearly_data = team_batting(year)
            yearly_data['Season'] = year
            data = pd.concat([data, yearly_data], ignore_index=True)
        except Exception as e:
            print(f"  Error fetching {year}: {e}")
            
    return data

def fetch_game_logs(teams_list, start_year, end_year):
    print(f"\nFetching game logs ({start_year}-{end_year})...")
    all_logs = []
    
    for year in range(start_year, end_year + 1):
        if year == 2020: continue
        
        print(f"  Processing {year}...")
        for team in teams_list:
            try:
                logs = schedule_and_record(year, team)
                logs['Team'] = team
                logs['Season'] = year
                cols_to_keep = ['Date', 'Team', 'Season', 'Opp', 'R', 'RA', 'W/L', 'Rank']
                available_cols = [c for c in cols_to_keep if c in logs.columns]
                all_logs.append(logs[available_cols])
                
                time.sleep(1.0) 
            except Exception:
                continue
                
    return pd.concat(all_logs, ignore_index=True)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_raw = os.path.join(project_root, "data", "raw")

    START_YEAR = 2015
    END_YEAR = 2025
    
    season_stats = fetch_season_aggregates(START_YEAR, END_YEAR)
    season_stats.to_csv(os.path.join(output_raw, "season_stats_raw.csv"), index=False)
    print("Season stats saved.")

    unique_teams = season_stats['Team'].unique().tolist()
    game_logs = fetch_game_logs(unique_teams, START_YEAR, END_YEAR)
    game_logs.to_csv(os.path.join(output_raw, "game_logs_raw.csv"), index=False)
    print("Game logs saved.")