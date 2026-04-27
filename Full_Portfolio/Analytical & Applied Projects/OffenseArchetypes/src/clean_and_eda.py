import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

def clean_fangraphs_df(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            if df[col].astype(str).str.contains('%').any():
                try:
                    df[col] = df[col].str.replace('%', '').astype(float) / 100
                except:
                    pass

    df.columns = [c.strip() for c in df.columns]
    
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    duplicates = [column for column in upper.columns if any(upper[column] > 0.999)]
    
    if duplicates:
        print(f"Dropping {len(duplicates)} redundant columns")
        df = df.drop(columns=duplicates)

    return df

def analyze_missing_data(df, name):
    print(f"\nMissing data report: {name}")
    
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    
    if missing.empty:
        print("No missing values")
    else:
        print(f"Found {len(missing)} columns with missing values")
        print(missing.sort_values(ascending=False).head(10))
        
        if 'Barrels' in df.columns:
            print("\nStatcast availability (Barrels missing per year):")
            print(df.groupby('Season')['Barrels'].apply(lambda x: x.isnull().sum()))

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    print("Loading data...")
    reg = pd.read_csv(os.path.join(raw_dir, "reg_season_all.csv"))
    post = pd.read_csv(os.path.join(raw_dir, "postseason_all.csv"))

    print("Cleaning regular season data...")
    reg_clean = clean_fangraphs_df(reg)
    
    print("Cleaning postseason data...")
    post_clean = clean_fangraphs_df(post)

    analyze_missing_data(reg_clean, "Regular Season")
    analyze_missing_data(post_clean, "Postseason")

    reg_path = os.path.join(processed_dir, "reg_season_clean.csv")
    post_path = os.path.join(processed_dir, "postseason_clean.csv")
    
    reg_clean.to_csv(reg_path, index=False)
    post_clean.to_csv(post_path, index=False)
    
    print(f"\nFiles saved:")
    print(f"  {reg_path} ({reg_clean.shape})")
    print(f"  {post_path} ({post_clean.shape})")