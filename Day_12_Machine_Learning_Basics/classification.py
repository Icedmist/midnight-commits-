#!/usr/bin/env python3
"""
Classification Model Implementation
A complete classification model implementation with multiple algorithms.
Features: Logistic regression, decision trees, random forests, and model evaluation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import classification_report, roc_curve, auc
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
import argparse
import sys
import seaborn as sns


class Classifier:
    """A multi-algorithm classification model."""

    def __init__(self, algorithm='logistic'):
        """Initialize the classifier with specified algorithm."""
        self.algorithm = algorithm
        self.model = self._get_model()
        self.scaler = StandardScaler()
        self.feature_names = None

    def _get_model(self):
        """Get the appropriate model based on algorithm."""
        if self.algorithm == 'logistic':
            return LogisticRegression(random_state=42, max_iter=1000)
        elif self.algorithm == 'decision_tree':
            return DecisionTreeClassifier(random_state=42)
        elif self.algorithm == 'random_forest':
            return RandomForestClassifier(random_state=42, n_estimators=100)
        elif self.algorithm == 'svm':
            return SVC(random_state=42, probability=True)
        else:
            raise ValueError("Unsupported algorithm")

    def fit(self, X, y):
        """Fit the classification model."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        self.model.fit(X_scaled, y)

    def predict(self, X):
        """Make predictions using the trained model."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X):
        """Get prediction probabilities."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def evaluate(self, X_test, y_test):
        """Evaluate the model performance."""
        y_pred = self.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        return {
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        }

    def cross_validate(self, X, y, cv=5):
        """Perform cross-validation."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_scaled = self.scaler.fit_transform(X)
        scores = cross_val_score(self.model, X_scaled, y, cv=cv, scoring='accuracy')
        return scores

    def print_summary(self):
        """Print model summary."""
        print(f"Classification Model Summary ({self.algorithm})")
        print("=" * 50)

        if hasattr(self.model, 'coef_'):
            print("Coefficients:")
            if self.feature_names:
                for name, coef in zip(self.feature_names, self.model.coef_[0]):
                    print(f"  {name}: {coef:.4f}")
            else:
                for i, coef in enumerate(self.model.coef_[0]):
                    print(f"  Feature {i}: {coef:.4f}")

        if hasattr(self.model, 'feature_importances_'):
            print("Feature Importances:")
            if self.feature_names:
                for name, importance in zip(self.feature_names, self.model.feature_importances_):
                    print(f"  {name}: {importance:.4f}")
            else:
                for i, importance in enumerate(self.model.feature_importances_):
                    print(f"  Feature {i}: {importance:.4f}")

    def plot_confusion_matrix(self, X_test, y_test, save_path=None):
        """Plot confusion matrix."""
        y_pred = self.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=np.unique(y_test), yticklabels=np.unique(y_test))
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')

        if save_path:
            plt.savefig(save_path)
            print(f"Confusion matrix saved to {save_path}")
        else:
            plt.show()

    def plot_roc_curve(self, X_test, y_test, save_path=None):
        """Plot ROC curve for binary classification."""
        if len(np.unique(y_test)) == 2:
            y_proba = self.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            roc_auc = auc(fpr, tpr)

            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Receiver Operating Characteristic (ROC) Curve')
            plt.legend(loc="lower right")

            if save_path:
                plt.savefig(save_path)
                print(f"ROC curve saved to {save_path}")
            else:
                plt.show()
        else:
            print("ROC curve is only available for binary classification")


def load_and_preprocess_data(file_path, target_column, test_size=0.2):
    """Load and preprocess data for classification."""
    # Load data
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    else:
        raise ValueError("Only CSV files are supported")

    print(f"Loaded data with shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")

    # Separate features and target
    X = data.drop(target_column, axis=1)
    y = data[target_column]

    # Handle categorical variables
    X = pd.get_dummies(X, drop_first=True)

    print(f"Features after preprocessing: {list(X.columns)}")
    print(f"Target classes: {np.unique(y)}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)

    return X_train, X_test, y_train, y_test


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Classification Tool")
    parser.add_argument("file_path", help="Path to the CSV data file")
    parser.add_argument("target_column", help="Name of the target column")
    parser.add_argument("--algorithm", choices=['logistic', 'decision_tree', 'random_forest', 'svm'],
                       default='logistic', help="Classification algorithm (default: logistic)")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size (default: 0.2)")
    parser.add_argument("--cv", type=int, default=5, help="Cross-validation folds (default: 5)")
    parser.add_argument("--plot", action="store_true", help="Generate plots")
    parser.add_argument("--save-plot", help="Save plots to specified path")

    args = parser.parse_args()

    try:
        # Load and preprocess data
        X_train, X_test, y_train, y_test = load_and_preprocess_data(
            args.file_path, args.target_column, args.test_size
        )

        # Train model
        classifier = Classifier(args.algorithm)
        classifier.fit(X_train, y_train)

        # Print summary
        classifier.print_summary()

        # Evaluate model
        metrics = classifier.evaluate(X_test, y_test)
        print("\nModel Evaluation:")
        print("-" * 20)
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")

        # Cross-validation
        cv_scores = classifier.cross_validate(X_train, y_train, args.cv)
        print(f"\nCross-validation scores: {cv_scores}")
        print(f"Mean CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        # Detailed classification report
        y_pred = classifier.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Generate plots if requested
        if args.plot or args.save_plot:
            classifier.plot_confusion_matrix(X_test, y_test, save_path=args.save_plot)
            classifier.plot_roc_curve(X_test, y_test, save_path=f"{args.save_plot}_roc" if args.save_plot else None)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()