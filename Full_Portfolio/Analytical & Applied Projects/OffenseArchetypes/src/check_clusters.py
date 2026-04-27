import pandas as pd
import os

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_path = os.path.join(project_root, "data", "processed", "clustered_teams.csv")
    
    df = pd.read_csv(input_path)
    
    if df['G'].mean() > 2000:
        df['Runs_Per_Game'] = df['R'] / 162
    else:
        df['Runs_Per_Game'] = df['R'] / df['G']

    cluster_names = {
        0: "Speed/Balanced",
        1: "Power",
        2: "Contact/Doubles"
    }
    
    print("Cluster assignments:")
    
    targets = [('TEX', 2023), ('ATL', 2023), ('TOR', 2025), ('MIL', 2025), ('ARI', 2023)]
    
    for team, year in targets:
        match = df[(df['Team'] == team) & (df['Season'] == year)]
        if not match.empty:
            c_id = match.iloc[0]['Cluster']
            name = cluster_names.get(c_id, f"Cluster {c_id}")
            print(f"{team} {year}: Cluster {c_id} ({name})")
            print(f"  HR_Share_Z: {match.iloc[0]['HR_Run_Share_Z']:.2f} | Gap_Z: {match.iloc[0]['Gap_Power_Z']:.2f} | BsR_Z: {match.iloc[0]['Baserunning_Value_Z']:.2f}")
        else:
            print(f"{team} {year}: Not found in model data")

    print("\nTop 5 teams per cluster (by runs per game):")
    for c_id in sorted(df['Cluster'].unique()):
        name = cluster_names.get(c_id, f"Cluster {c_id}")
        print(f"\n{name}:")
        top_teams = df[df['Cluster'] == c_id].sort_values('Runs_Per_Game', ascending=False).head(5)
        for i, row in top_teams.iterrows():
            print(f"  {row['Team']} {row['Season']} - {row['Runs_Per_Game']:.2f} R/G")