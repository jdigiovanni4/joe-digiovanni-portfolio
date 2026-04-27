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
    if optimal_k < 4: optimal_k = 4 

    plt.figure(figsize=(10, 6))
    plt.plot(n_components, bics, marker='o', color='black')
    plt.axvline(optimal_k, color='red', linestyle='--', label=f'Selected k={optimal_k}')
    plt.title('Model Selection: BIC Score', fontsize=14)
    plt.grid(True, alpha=0.3)
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

def visualize_pca_style(df, loadings, output_file):
    plt.figure(figsize=(14, 10))
    sns.set_style("whitegrid")
    
    sns.scatterplot(
        data=df, x='PC1', y='PC2', hue='Cluster', 
        palette='bright', s=150, alpha=0.8, edgecolor='black'
    )
    
    targets = [('TEX', 2023), ('TOR', 2025), ('ATL', 2023), ('MIL', 2025), ('ARI', 2023)]
    for team, year in targets:
        subset = df[(df['Team'] == team) & (df['Season'] == year)]
        if not subset.empty:
            plt.text(subset.iloc[0]['PC1'], subset.iloc[0]['PC2']+0.25, 
                     f"{team} '{str(year)[2:]}", 
                     ha='center', fontsize=10, weight='bold', 
                     bbox=dict(facecolor='white', edgecolor='black', alpha=0.9))

    for i, feature in enumerate(loadings.index):
        x = loadings.iloc[i]['PC1'] * 4.0
        y = loadings.iloc[i]['PC2'] * 4.0
        plt.arrow(0, 0, x, y, color='#E31937', alpha=0.5, width=0.005, head_width=0.08)
        label_map = {'HR_Run_Share_Z': 'HR Rely', 'Contact_Ability_Z': 'Contact', 'Gap_Power_Z': 'Gap (2B)', 'Baserunning_Value_Z': 'BsR', 'ISO_Z': 'ISO'}
        plt.text(x*1.1, y*1.1, label_map.get(feature, feature), color='darkred', fontsize=10, weight='bold')

    plt.title('Offensive Style Map', fontsize=16)
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_path = os.path.join(project_root, "data", "processed", "team_features_advanced.csv")
    out_dir = os.path.join(project_root, "data", "processed")
    img_dir = os.path.join(project_root, "notebooks")
    
    df = pd.read_csv(input_path)
    
    features = [
        'HR_Run_Share_Z',
        'Contact_Ability_Z',
        'Gap_Power_Z',
        'Baserunning_Value_Z',
        'ISO_Z'
    ]
    
    if 'ISO_Z' not in df.columns:
        print("Error: ISO_Z not found. Re-run feature_engineering.py")
        exit()

    model_data = df.dropna(subset=features).copy()
    X = model_data[features]
    
    print("Calculating optimal clusters...")
    optimal_k = plot_bic_scores(X, 10, os.path.join(img_dir, "model_selection_bic.png"))
    print(f"Optimal clusters: {optimal_k}")
    
    print(f"Fitting GMM with k={optimal_k}...")
    gmm = GaussianMixture(n_components=optimal_k, random_state=42, n_init=10)
    model_data['Cluster'] = gmm.fit_predict(X)
    
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    model_data['PC1'] = coords[:, 0]
    model_data['PC2'] = coords[:, 1]
    
    loadings = pd.DataFrame(pca.components_.T, columns=['PC1', 'PC2'], index=features)
    
    model_data.to_csv(os.path.join(out_dir, "clustered_teams.csv"), index=False)
    visualize_pca_style(model_data, loadings, os.path.join(img_dir, "archetype_map.png"))
    visualize_cluster_profiles(model_data, features, os.path.join(img_dir, "cluster_heatmap.png"))
    
    print("Analysis complete.")