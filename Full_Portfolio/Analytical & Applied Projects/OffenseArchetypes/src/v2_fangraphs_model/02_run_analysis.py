import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA

def plot_bic_scores(X, max_k, output_file):
    n_components = range(1, max_k + 1)
    models = [GaussianMixture(n, covariance_type='full', random_state=42).fit(X) for n in n_components]
    bics = [m.bic(X) for m in models]
    
    optimal_k = np.argmin(bics) + 1
    if optimal_k < 3: optimal_k = 3

    plt.figure(figsize=(10, 6))
    plt.plot(n_components, bics, marker='o', color='black')
    plt.axvline(optimal_k, color='red', linestyle='--', label=f'Selected k={optimal_k}')
    plt.title('Model Selection (BIC)', fontsize=14)
    plt.savefig(output_file)
    plt.close()
    return optimal_k

def visualize_cluster_profiles(df, features, output_file):
    profile = df.groupby('Cluster')[features].mean()
    plt.figure(figsize=(12, 8))
    sns.heatmap(profile, annot=True, cmap='RdBu_r', center=0, fmt='.2f', linewidths=.5, linecolor='black')
    plt.title('Cluster Feature Profiles', fontsize=16)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def visualize_pca_map(df, loadings, output_file):
    plt.figure(figsize=(14, 10))
    sns.set_style("whitegrid")
    
    sns.scatterplot(
        data=df, x='PC1', y='PC2', hue='Cluster', 
        palette='bright', s=120, alpha=0.8, edgecolor='black'
    )
    
    targets = [('TEX', 2023), ('TOR', 2025), ('ATL', 2023), ('ARI', 2023)]
    for team, year in targets:
        subset = df[(df['Team'] == team) & (df['Season'] == year)]
        if not subset.empty:
            plt.text(subset.iloc[0]['PC1'], subset.iloc[0]['PC2']+0.2, f"{team} '{str(year)[2:]}", 
                     ha='center', fontsize=10, weight='bold', 
                     bbox=dict(facecolor='white', edgecolor='black', alpha=0.9))

    for i, feature in enumerate(loadings.index):
        x = loadings.iloc[i]['PC1'] * 3.5
        y = loadings.iloc[i]['PC2'] * 3.5
        plt.arrow(0, 0, x, y, color='red', alpha=0.5, width=0.005, head_width=0.08)
        label = feature.replace('_Z', '').replace('Pct', '%')
        plt.text(x*1.1, y*1.1, label, color='darkred', fontsize=9)

    plt.title('Offensive Style Map', fontsize=16)
    plt.savefig(output_file)
    plt.close()

def clean_and_prepare_data(df, is_postseason=False):
    df.columns = [c.strip().replace('%', 'Pct') for c in df.columns]
    
    if 'Base Running' in df.columns and 'BsR' not in df.columns:
        df = df.rename(columns={'Base Running': 'BsR'})

    for col in df.columns:
        if df[col].dtype == 'object' and df[col].str.contains('%', na=False).any():
            try:
                df[col] = pd.to_numeric(df[col].str.replace('%', ''), errors='coerce') / 100
            except:
                pass
            
    numeric_cols = ['BarrelPct', 'KPct', 'GB/FB', 'BsR', 'Z-SwingPct', 'O-SwingPct', 'wRC+']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def validate_postseason(clustered_df, post_df, output_file):
    post_clean = clean_and_prepare_data(post_df, is_postseason=True)
    
    merged = clustered_df.merge(post_clean[['Season', 'Team', 'wRC+']], on=['Season', 'Team'], how='inner', suffixes=('_reg', '_post'))
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=merged, x='Cluster', y='wRC+_post', palette='bright')
    sns.stripplot(data=merged, x='Cluster', y='wRC+_post', color='black', alpha=0.4)
    plt.axhline(100, color='red', linestyle='--', label='League Average')
    plt.title('Postseason Performance by Cluster', fontsize=14)
    plt.ylabel('Postseason wRC+', fontsize=12)
    plt.xlabel('Cluster ID', fontsize=12)
    plt.legend()
    plt.savefig(output_file)
    plt.close()
    
    return merged.groupby('Cluster')['wRC+_post'].median()


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    processed_dir = os.path.join(project_root, "data", "processed")
    raw_dir = os.path.join(project_root, "data", "raw")
    img_dir = os.path.join(project_root, "notebooks")
    os.makedirs(img_dir, exist_ok=True)

    features_path = os.path.join(processed_dir, "fangraphs_features_master.csv")
    df = pd.read_csv(features_path)

    features_z = [
        'BarrelPct_Z', 'Contact_Skill_Z', 'GB/FB_Z',
        'BsR_Z', 'Discipline_Ratio_Z'
    ]
    model_data = df.dropna(subset=features_z).copy()
    X = model_data[features_z]
    
    print("Calculating optimal cluster count...")
    optimal_k = plot_bic_scores(X, 8, os.path.join(img_dir, "v2_bic_plot.png"))
    print(f"Optimal clusters: {optimal_k}")

    print(f"Fitting GMM with k={optimal_k}...")
    gmm = GaussianMixture(n_components=optimal_k, random_state=42, n_init=10)
    model_data['Cluster'] = gmm.fit_predict(X)
    
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    model_data['PC1'] = coords[:, 0]
    model_data['PC2'] = coords[:, 1]
    
    loadings = pd.DataFrame(pca.components_.T, columns=['PC1', 'PC2'], index=features_z)
    
    visualize_cluster_profiles(model_data, features_z, os.path.join(img_dir, "v2_heatmap.png"))
    visualize_pca_map(model_data, loadings, os.path.join(img_dir, "v2_archetype_map.png"))
    
    print("Validating against postseason performance...")
    post_df = pd.read_csv(os.path.join(raw_dir, "postseason_all.csv"))
    postseason_results = validate_postseason(model_data, post_df, os.path.join(img_dir, "v2_postseason_validation.png"))
    
    print("\nMedian postseason wRC+ by cluster:")
    print(postseason_results)
    
    out_path = os.path.join(processed_dir, "fangraphs_clustered.csv")
    model_data.to_csv(out_path, index=False)
    print(f"\nAnalysis complete. Data saved to {out_path}")