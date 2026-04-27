import pandas as pd
import os

def name_clusters(df):
    profile = df.groupby('Cluster').mean(numeric_only=True)
    
    power_cluster_id = profile['BarrelPct_Z'].idxmax()
    chaos_cluster_id = profile['BsR_Z'].idxmax()
    gb_cluster_id = profile['GB/FB_Z'].idxmax()

    cluster_names = {
        power_cluster_id: "Power",
        chaos_cluster_id: "Speed/Contact",
    }

    for cid in profile.index:
        if cid not in cluster_names:
            if profile.loc[cid]['BarrelPct_Z'] < -0.2 and profile.loc[cid]['BsR_Z'] < -0.2:
                 cluster_names[cid] = "Low Production"
            else:
                 cluster_names[cid] = "Balanced"
                 
    return cluster_names

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    input_path = os.path.join(project_root, "data", "processed", "fangraphs_clustered.csv")
    
    if not os.path.exists(input_path):
        print(f"Error: Clustered data not found at {input_path}")
        print("Run '02_run_analysis.py' first.")
        exit()

    df = pd.read_csv(input_path)
    cluster_names = name_clusters(df)
    
    print("Top 5 seasons by archetype (ranked by wRC+)")
    print("=" * 60)
    
    for cluster_id in sorted(cluster_names.keys()):
        cluster_name = cluster_names[cluster_id]
        teams_in_cluster = df[df['Cluster'] == cluster_id]
        top_performers = teams_in_cluster.sort_values('wRC+', ascending=False).head(5)
        
        print(f"\n{cluster_name}:")
        
        if top_performers.empty:
            print("  No teams found")
            continue
            
        for i, row in top_performers.iterrows():
            barrel_z = row.get('BarrelPct_Z', 0)
            bsr_z = row.get('BsR_Z', 0)
            contact_z = row.get('Contact_Skill_Z', 0)
            
            print(f"  {row['Season']} {row['Team']:<3} | {row['wRC+']:>3.0f} wRC+ (Barrel: {barrel_z:+.1f}σ, Speed: {bsr_z:+.1f}σ, Contact: {contact_z:+.1f}σ)")