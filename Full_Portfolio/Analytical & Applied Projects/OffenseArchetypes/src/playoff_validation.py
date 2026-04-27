import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def analyze_october_performance(model_df, playoff_df):
    print("Columns found:", playoff_df.columns.tolist())
    
    playoff_df.columns = [c.strip() for c in playoff_df.columns]
    
    if 'wRC+' in playoff_df.columns:
        playoff_df['wRC+'] = pd.to_numeric(playoff_df['wRC+'], errors='coerce')
        
    merged = model_df.merge(playoff_df, on=['Team', 'Season'], how='inner')
    
    return merged

def visualize_playoff_wrc(df, output_file):
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    sns.boxplot(data=df, x='Cluster', y='wRC+', palette='bright')
    sns.stripplot(data=df, x='Cluster', y='wRC+', color='black', alpha=0.5)
    
    plt.axhline(100, color='red', linestyle='--', label='League Average (100)')
    
    plt.title('Postseason Performance by Cluster', fontsize=14)
    plt.ylabel('Postseason wRC+', fontsize=12)
    plt.xlabel('Cluster ID', fontsize=12)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_path = os.path.join(project_root, "data", "processed", "clustered_teams.csv")
    post_path = os.path.join(project_root, "data", "raw", "postseason_data.csv")
    output_img = os.path.join(project_root, "notebooks", "playoff_performance.png")
    
    df = pd.read_csv(input_path)
    
    if not os.path.exists(post_path):
        print(f"Error: File not found at {post_path}")
        exit()
        
    try:
        post_df = pd.read_csv(post_path)
    except Exception as e:
        print("Error reading CSV file")
        exit()
    
    print("Merging data...")
    final_df = analyze_october_performance(df, post_df)
    
    if not final_df.empty:
        print("\nMedian postseason wRC+ by cluster:")
        summary = final_df.groupby('Cluster')['wRC+'].median().sort_values(ascending=False)
        print(summary)
        
        print("\nTeams with wRC+ < 80 by cluster:")
        chokers = final_df[final_df['wRC+'] < 80].groupby('Cluster')['Team'].count()
        print(chokers)

        visualize_playoff_wrc(final_df, output_img)
        print(f"\nAnalysis saved to {output_img}")
    else:
        print("Merge failed. Check team abbreviations in CSV.")