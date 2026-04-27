import pandas as pd
import numpy as np
import os
import warnings
from pybaseball import batting_stats

warnings.simplefilter(action='ignore', category=FutureWarning)

def clean_aggregates(df):
    numeric_cols = ['R', 'HR', 'G', 'PA', 'H', 'BB', 'SO', '2B', '3B', 'BsR', 'SLG', 'AVG']
    
    clean_df = df.copy()
    for col in numeric_cols:
        if col in clean_df.columns and clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).str.replace(r'[%,]', '', regex=True)
            clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
    
    if 'BsR' not in clean_df.columns:
        clean_df['BsR'] = clean_df.get('SB', 0)
        
    return clean_df

def calculate_gini(array):
    array = array.flatten().astype(float)
    if np.amin(array) < 0:
        array -= np.amin(array)
    array += 0.0000001 
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return ((2 * index - n - 1) * array).sum() / (n * array.sum())

def get_lineup_balance_metrics(start_year, end_year):
    return pd.DataFrame() 

def engineer_features(stats_df, logs_df):
    stats_df['Traffic_Per_Game'] = (stats_df['H'] + stats_df['BB']) / stats_df['G']
    stats_df['HR_Run_Share'] = (stats_df['HR'] * 1.6) / stats_df['R']
    stats_df['Contact_Ability'] = 1 - (stats_df['SO'] / stats_df['PA'])
    
    stats_df['Gap_Power'] = (stats_df['2B'] + stats_df['3B']) / stats_df['G']
    stats_df['Baserunning_Value'] = stats_df['BsR'] / stats_df['G']
    stats_df['ISO'] = stats_df['SLG'] - stats_df['AVG']

    consistency_data = []
    groups = logs_df.groupby(['Team', 'Season'])
    for (team, season), group in groups:
        runs = pd.to_numeric(group['R'], errors='coerce').dropna()
        if len(runs) < 50: continue
        consistency_data.append({
            'Team': team, 'Season': season,
            'Run_StdDev': runs.std(),
            'Blowout_Pct': (runs >= 5).mean(),
            'Dud_Pct': (runs <= 1).mean()
        })
    consistency_df = pd.DataFrame(consistency_data)
    
    return pd.merge(stats_df, consistency_df, on=['Team', 'Season'], how='inner')

def apply_era_normalization(df, features_to_norm):
    df_norm = df.copy()
    for col in features_to_norm:
        df_norm[f'{col}_Z'] = df.groupby('Season')[col].transform(lambda x: (x - x.mean()) / x.std())
    return df_norm

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    season_raw = pd.read_csv(os.path.join(raw_dir, "season_stats_raw.csv"))
    logs_raw = pd.read_csv(os.path.join(raw_dir, "game_logs_raw.csv"))
    
    season_clean = clean_aggregates(season_raw)
    final_df = engineer_features(season_clean, logs_raw)
    
    cols_to_normalize = [
        'HR_Run_Share', 'Contact_Ability', 'Gap_Power', 'Baserunning_Value', 'ISO'
    ]
    final_df = apply_era_normalization(final_df, cols_to_normalize)

    out_path = os.path.join(processed_dir, "team_features_advanced.csv")
    final_df.to_csv(out_path, index=False)
    print(f"Feature engineering complete. Output: {out_path}")