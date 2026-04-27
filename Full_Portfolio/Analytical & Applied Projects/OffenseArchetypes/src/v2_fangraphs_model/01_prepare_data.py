import pandas as pd
import numpy as np
import os

def clean_and_prepare_data(df):
    df.columns = [c.strip().replace('%', 'Pct') for c in df.columns]
    
    if 'Base Running' in df.columns and 'BsR' not in df.columns:
        df = df.rename(columns={'Base Running': 'BsR'})

    for col in df.columns:
        if df[col].dtype == 'object' and df[col].str.contains('%', na=False).any():
            try:
                df[col] = pd.to_numeric(df[col].str.replace('%', ''), errors='coerce') / 100
            except:
                pass
            
    numeric_cols = ['BarrelPct', 'KPct', 'GB/FB', 'BsR', 'Z-SwingPct', 'O-SwingPct']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def engineer_features(df):
    df['Contact_Skill'] = 1 - df['KPct']
    df['Discipline_Ratio'] = df['Z-SwingPct'] / (df['O-SwingPct'] + 0.001)
    return df

def apply_era_normalization(df, features_to_norm):
    df_norm = df.copy()
    for col in features_to_norm:
        if col in df_norm.columns:
            df_norm[f'{col}_Z'] = df.groupby('Season')[col].transform(lambda x: (x - x.mean()) / x.std())
    return df_norm

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    try:
        reg_df = pd.read_csv(os.path.join(raw_dir, "reg_season_all.csv"))
    except FileNotFoundError:
        print(f"Error: File not found at {os.path.join(raw_dir, 'reg_season_all.csv')}")
        exit()
    
    reg_clean = clean_and_prepare_data(reg_df)
    reg_features = engineer_features(reg_clean)

    cols_to_normalize = ['BarrelPct', 'Contact_Skill', 'GB/FB', 'BsR', 'Discipline_Ratio']
    reg_final = apply_era_normalization(reg_features, cols_to_normalize)
    
    out_path = os.path.join(processed_dir, "fangraphs_features_master.csv")
    reg_final.to_csv(out_path, index=False)
    
    print(f"Feature file created: {out_path}")