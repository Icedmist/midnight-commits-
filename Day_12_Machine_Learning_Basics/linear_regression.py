#!/usr/bin/env python3
"""
Linear Regression Implementation
A complete linear regression model implementation with training and prediction.
Features: Simple and multiple linear regression, evaluation metrics, and visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import argparse
import sys


class LinearRegressor:
    """A linear regression model implementation."""

    def __init__(self):
        """Initialize the linear regression model."""
        self.model = LinearRegression()
        self.coefficients = None
        self.intercept = None
        self.feature_names = None

    def fit(self, X, y):
        """Fit the linear regression model."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        self.model.fit(X, y)
        self.coefficients = self.model.coef_
        self.intercept = self.model.intercept_

    def predict(self, X):
        """Make predictions using the trained model."""
        if isinstance(X, pd.DataFrame):
            X = X.values
        return self.model.predict(X)

    def evaluate(self, X_test, y_test):
        """Evaluate the model performance."""
        y_pred = self.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        return {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R²': r2
        }

    def print_summary(self):
        """Print model summary."""
        print("Linear Regression Model Summary")
        print("=" * 40)
        print(f"Intercept: {self.intercept:.4f}")
        print("Coefficients:")
        if self.feature_names:
            for name, coef in zip(self.feature_names, self.coefficients):
                print(f"  {name}: {coef:.4f}")
        else:
            for i, coef in enumerate(self.coefficients):
                print(f"  Feature {i}: {coef:.4f}")

    def plot_residuals(self, X_test, y_test, save_path=None):
        """Plot residuals to check model assumptions."""
        y_pred = self.predict(X_test)
        residuals = y_test - y_pred

        plt.figure(figsize=(10, 6))

        plt.subplot(1, 2, 1)
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.xlabel('Predicted Values')
        plt.ylabel('Residuals')
        plt.title('Residuals vs Predicted Values')
        plt.axhline(y=0, color='r', linestyle='--')

        plt.subplot(1, 2, 2)
        plt.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        plt.title('Residuals Distribution')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Residual plot saved to {save_path}")
        else:
            plt.show()

    def plot_predictions(self, X_test, y_test, feature_index=0, save_path=None):
        """Plot actual vs predicted values for a single feature."""
        if X_test.shape[1] > 1:
            # For multiple features, plot against the specified feature
            X_plot = X_test[:, feature_index]
            feature_name = self.feature_names[feature_index] if self.feature_names else f"Feature {feature_index}"
        else:
            X_plot = X_test.flatten()
            feature_name = self.feature_names[0] if self.feature_names else "Feature"

        y_pred = self.predict(X_test)

        plt.figure(figsize=(8, 6))
        plt.scatter(X_plot, y_test, alpha=0.5, label='Actual')
        plt.scatter(X_plot, y_pred, alpha=0.5, label='Predicted', color='red')

        # Plot regression line
        if X_test.shape[1] == 1:
            X_line = np.linspace(X_plot.min(), X_plot.max(), 100).reshape(-1, 1)
            y_line = self.predict(X_line)
            plt.plot(X_line.flatten(), y_line, color='green', linewidth=2, label='Regression Line')

        plt.xlabel(feature_name)
        plt.ylabel('Target')
        plt.title('Actual vs Predicted Values')
        plt.legend()

        if save_path:
            plt.savefig(save_path)
            print(f"Prediction plot saved to {save_path}")
        else:
            plt.show()


def load_and_preprocess_data(file_path, target_column, test_size=0.2):
    """Load and preprocess data for linear regression."""
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

    # Handle categorical variables (simple approach)
    X = pd.get_dummies(X, drop_first=True)

    print(f"Features after preprocessing: {list(X.columns)}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    return X_train, X_test, y_train, y_test


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Linear Regression Tool")
    parser.add_argument("file_path", help="Path to the CSV data file")
    parser.add_argument("target_column", help="Name of the target column")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size (default: 0.2)")
    parser.add_argument("--plot", action="store_true", help="Generate plots")
    parser.add_argument("--save-plot", help="Save plots to specified path")

    args = parser.parse_args()

    try:
        # Load and preprocess data
        X_train, X_test, y_train, y_test = load_and_preprocess_data(
            args.file_path, args.target_column, args.test_size
        )

        # Train model
        regressor = LinearRegressor()
        regressor.fit(X_train, y_train)

        # Print summary
        regressor.print_summary()

        # Evaluate model
        metrics = regressor.evaluate(X_test, y_test)
        print("\nModel Evaluation:")
        print("-" * 20)
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")

        # Generate plots if requested
        if args.plot or args.save_plot:
            if X_test.shape[1] == 1:
                regressor.plot_predictions(X_test, y_test, save_path=args.save_plot)
            regressor.plot_residuals(X_test, y_test, save_path=f"{args.save_plot}_residuals" if args.save_plot else None)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()