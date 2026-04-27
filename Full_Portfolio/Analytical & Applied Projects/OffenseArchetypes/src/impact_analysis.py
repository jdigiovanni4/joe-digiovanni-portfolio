import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def analyze_offensive_output(df):
    if df['G'].mean() > 2000:
        df['Runs_Per_Game'] = df['R'] / 162
    else:
        df['Runs_Per_Game'] = df['R'] / df['G']

    summary = df.groupby('Cluster').agg(
        Teams=('Team', 'count'),
        Runs_Per_Game=('Runs_Per_Game', 'mean'),
        Run_Volatility=('Run_StdDev', 'mean'), 
        Blowout_Rate=('Blowout_Pct', 'mean'),
        Dud_Rate=('Dud_Pct', 'mean')
    ).reset_index()
    
    summary['Runs_Per_Game'] = summary['Runs_Per_Game'].round(2)
    summary['Run_Volatility'] = summary['Run_Volatility'].round(2)
    summary['Blowout_Rate'] = (summary['Blowout_Rate'] * 100).round(1)
    summary['Dud_Rate'] = (summary['Dud_Rate'] * 100).round(1)
    
    return summary

def visualize_impact_distributions(df, output_file):
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    sns.boxplot(
        data=df, x='Cluster', y='Runs_Per_Game', 
        palette='bright', showfliers=False
    )
    sns.stripplot(
        data=df, x='Cluster', y='Runs_Per_Game', 
        color='black', alpha=0.3, jitter=True
    )
    
    plt.title('Offensive Output by Cluster', fontsize=14)
    plt.ylabel('Runs Per Game', fontsize=12)
    plt.xlabel('Cluster ID', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_path = os.path.join(project_root, "data", "processed", "clustered_teams.csv")
    output_img = os.path.join(project_root, "notebooks", "archetype_production.png")

    df = pd.read_csv(input_path)
    
    if 'Runs_Per_Game' not in df.columns:
        df['Runs_Per_Game'] = df['R'] / df['G']
        
    summary_stats = analyze_offensive_output(df)
    
    print("\nProduction summary by cluster:")
    print(summary_stats.to_string(index=False))
    
    visualize_impact_distributions(df, output_img)
    print(f"\nVisualization saved to {output_img}")