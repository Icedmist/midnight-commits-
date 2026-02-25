#!/usr/bin/env python3
"""
Clustering Algorithms Implementation
A complete clustering analysis toolkit with K-means, hierarchical, and DBSCAN.
Features: Multiple clustering algorithms, evaluation metrics, and visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage
import argparse
import sys
import seaborn as sns


class ClusterAnalyzer:
    """A multi-algorithm clustering analyzer."""

    def __init__(self, algorithm='kmeans', **kwargs):
        """Initialize the cluster analyzer."""
        self.algorithm = algorithm
        self.model = self._get_model(**kwargs)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.labels = None
        self.feature_names = None

    def _get_model(self, **kwargs):
        """Get the appropriate clustering model."""
        if self.algorithm == 'kmeans':
            n_clusters = kwargs.get('n_clusters', 3)
            return KMeans(n_clusters=n_clusters, random_state=42, **kwargs)
        elif self.algorithm == 'hierarchical':
            n_clusters = kwargs.get('n_clusters', 3)
            linkage_type = kwargs.get('linkage', 'ward')
            return AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage_type, **kwargs)
        elif self.algorithm == 'dbscan':
            eps = kwargs.get('eps', 0.5)
            min_samples = kwargs.get('min_samples', 5)
            return DBSCAN(eps=eps, min_samples=min_samples, **kwargs)
        else:
            raise ValueError("Unsupported algorithm")

    def fit(self, X):
        """Fit the clustering model."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        self.labels = self.model.fit_predict(X_scaled)

        return self.labels

    def evaluate_clustering(self, X):
        """Evaluate clustering quality."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.transform(X)

        # Calculate metrics
        try:
            silhouette = silhouette_score(X_scaled, self.labels)
        except:
            silhouette = None

        try:
            ch_score = calinski_harabasz_score(X_scaled, self.labels)
        except:
            ch_score = None

        try:
            db_score = davies_bouldin_score(X_scaled, self.labels)
        except:
            db_score = None

        # Count clusters (excluding noise for DBSCAN)
        n_clusters = len(set(self.labels)) - (1 if -1 in self.labels else 0)
        n_noise = list(self.labels).count(-1) if -1 in self.labels else 0

        return {
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'silhouette_score': silhouette,
            'calinski_harabasz_score': ch_score,
            'davies_bouldin_score': db_score
        }

    def find_optimal_k(self, X, max_k=10, method='silhouette'):
        """Find optimal number of clusters using elbow method or silhouette analysis."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.fit_transform(X)

        scores = []
        k_values = range(2, max_k + 1)

        for k in k_values:
            if method == 'silhouette':
                kmeans = KMeans(n_clusters=k, random_state=42)
                labels = kmeans.fit_predict(X_scaled)
                score = silhouette_score(X_scaled, labels)
            elif method == 'inertia':
                kmeans = KMeans(n_clusters=k, random_state=42)
                kmeans.fit(X_scaled)
                score = kmeans.inertia_
            scores.append(score)

        # Find optimal k
        if method == 'silhouette':
            optimal_k = k_values[np.argmax(scores)]
        elif method == 'inertia':
            # Elbow method - find the "elbow"
            diffs = np.diff(scores)
            optimal_k = k_values[np.argmin(diffs) + 1]

        return optimal_k, dict(zip(k_values, scores))

    def plot_clusters(self, X, save_path=None):
        """Plot clusters using PCA for dimensionality reduction."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.fit_transform(X_scaled)

        plt.figure(figsize=(10, 8))

        # Plot clusters
        unique_labels = set(self.labels)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise
                col = 'black'

            class_member_mask = (self.labels == k)

            xy = X_pca[class_member_mask]
            plt.scatter(xy[:, 0], xy[:, 1], c=[col], alpha=0.6, s=50)

        plt.title(f'Clusters ({self.algorithm}) - PCA Projection')
        plt.xlabel('PC1')
        plt.ylabel('PC2')

        if save_path:
            plt.savefig(save_path)
            print(f"Cluster plot saved to {save_path}")
        else:
            plt.show()

    def plot_elbow_curve(self, X, max_k=10, save_path=None):
        """Plot elbow curve to find optimal k."""
        optimal_k, scores = self.find_optimal_k(X, max_k, method='inertia')

        plt.figure(figsize=(8, 6))
        plt.plot(list(scores.keys()), list(scores.values()), 'bo-')
        plt.axvline(x=optimal_k, color='r', linestyle='--', label=f'Optimal k={optimal_k}')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('Inertia')
        plt.title('Elbow Method for Optimal k')
        plt.legend()

        if save_path:
            plt.savefig(save_path)
            print(f"Elbow curve saved to {save_path}")
        else:
            plt.show()

    def plot_dendrogram(self, X, save_path=None):
        """Plot dendrogram for hierarchical clustering."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.fit_transform(X)

        plt.figure(figsize=(12, 8))
        linkage_matrix = linkage(X_scaled, method='ward')
        dendrogram(linkage_matrix)
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('Sample Index')
        plt.ylabel('Distance')

        if save_path:
            plt.savefig(save_path)
            print(f"Dendrogram saved to {save_path}")
        else:
            plt.show()

    def get_cluster_summary(self, X):
        """Get summary statistics for each cluster."""
        if isinstance(X, pd.DataFrame):
            X_original = X.copy()
            X = X.values

        summaries = {}

        for cluster_id in np.unique(self.labels):
            if cluster_id == -1:
                continue  # Skip noise

            mask = self.labels == cluster_id
            cluster_data = X[mask]

            summary = {
                'size': len(cluster_data),
                'centroid': cluster_data.mean(axis=0),
                'std': cluster_data.std(axis=0)
            }

            if isinstance(X_original, pd.DataFrame):
                # Add feature-wise statistics
                cluster_df = X_original[mask]
                summary['feature_means'] = cluster_df.mean()
                summary['feature_stds'] = cluster_df.std()

            summaries[f'Cluster_{cluster_id}'] = summary

        return summaries


def load_data(file_path):
    """Load data for clustering."""
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    else:
        raise ValueError("Only CSV files are supported")

    print(f"Loaded data with shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")

    # Assume all columns are features (no target for unsupervised learning)
    return data


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Clustering Analysis Tool")
    parser.add_argument("file_path", help="Path to the CSV data file")
    parser.add_argument("--algorithm", choices=['kmeans', 'hierarchical', 'dbscan'],
                       default='kmeans', help="Clustering algorithm (default: kmeans)")
    parser.add_argument("--n-clusters", type=int, default=3, help="Number of clusters (default: 3)")
    parser.add_argument("--eps", type=float, default=0.5, help="DBSCAN eps parameter (default: 0.5)")
    parser.add_argument("--min-samples", type=int, default=5, help="DBSCAN min_samples parameter (default: 5)")
    parser.add_argument("--find-optimal", action="store_true", help="Find optimal number of clusters")
    parser.add_argument("--plot", action="store_true", help="Generate plots")
    parser.add_argument("--save-plot", help="Save plots to specified path")

    args = parser.parse_args()

    try:
        # Load data
        data = load_data(args.file_path)

        # Initialize analyzer
        if args.algorithm == 'dbscan':
            analyzer = ClusterAnalyzer(args.algorithm, eps=args.eps, min_samples=args.min_samples)
        else:
            analyzer = ClusterAnalyzer(args.algorithm, n_clusters=args.n_clusters)

        # Fit model
        labels = analyzer.fit(data)

        # Evaluate clustering
        metrics = analyzer.evaluate_clustering(data)
        print("\nClustering Evaluation:")
        print("-" * 25)
        for metric, value in metrics.items():
            if value is not None:
                print(f"{metric}: {value:.4f}")
            else:
                print(f"{metric}: N/A")

        # Find optimal k if requested
        if args.find_optimal and args.algorithm == 'kmeans':
            optimal_k, scores = analyzer.find_optimal_k(data)
            print(f"\nOptimal number of clusters: {optimal_k}")

        # Get cluster summaries
        summaries = analyzer.get_cluster_summary(data)
        print("\nCluster Summaries:")
        for cluster_name, summary in summaries.items():
            print(f"{cluster_name}: {summary['size']} samples")

        # Generate plots if requested
        if args.plot or args.save_plot:
            analyzer.plot_clusters(data, save_path=args.save_plot)

            if args.algorithm == 'kmeans' and args.find_optimal:
                analyzer.plot_elbow_curve(data, save_path=f"{args.save_plot}_elbow" if args.save_plot else None)

            if args.algorithm == 'hierarchical':
                analyzer.plot_dendrogram(data, save_path=f"{args.save_plot}_dendrogram" if args.save_plot else None)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()