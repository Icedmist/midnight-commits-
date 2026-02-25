#!/usr/bin/env python3
"""
Data Preprocessing Utilities
A collection of data preprocessing functions for machine learning.
Features: Data cleaning, normalization, encoding, and feature engineering.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import argparse


class DataPreprocessor:
    """A class for preprocessing data for machine learning."""

    def __init__(self):
        """Initialize the preprocessor."""
        self.scalers = {}
        self.encoders = {}

    def load_data(self, file_path, **kwargs):
        """Load data from various file formats."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, **kwargs)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path, **kwargs)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path, **kwargs)
        else:
            raise ValueError("Unsupported file format")

    def handle_missing_values(self, df, strategy='mean', columns=None):
        """Handle missing values in the dataset."""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns

        imputer = SimpleImputer(strategy=strategy)
        df[columns] = imputer.fit_transform(df[columns])
        return df

    def remove_outliers(self, df, columns, method='iqr', threshold=1.5):
        """Remove outliers using IQR or Z-score method."""
        if method == 'iqr':
            for col in columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        elif method == 'zscore':
            for col in columns:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df = df[z_scores < threshold]
        return df

    def normalize_data(self, df, columns, method='standard'):
        """Normalize numerical data."""
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Invalid normalization method")

        df[columns] = scaler.fit_transform(df[columns])
        self.scalers[method] = scaler
        return df

    def encode_categorical(self, df, columns, method='label'):
        """Encode categorical variables."""
        for col in columns:
            if method == 'label':
                encoder = LabelEncoder()
                df[col] = encoder.fit_transform(df[col])
            elif method == 'onehot':
                # One-hot encoding returns multiple columns
                encoder = OneHotEncoder(sparse=False, drop='first')
                encoded = encoder.fit_transform(df[[col]])
                encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(encoded.shape[1])])
                df = pd.concat([df.drop(col, axis=1), encoded_df], axis=1)
            self.encoders[col] = encoder
        return df

    def feature_engineering(self, df):
        """Perform basic feature engineering."""
        # Add some example features
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 100], labels=['child', 'young', 'middle', 'senior'])

        if 'income' in df.columns and 'age' in df.columns:
            df['income_per_age'] = df['income'] / df['age']

        return df

    def split_data(self, X, y, test_size=0.2, random_state=42):
        """Split data into training and testing sets."""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    def preprocess_pipeline(self, file_path, target_column=None):
        """Complete preprocessing pipeline."""
        # Load data
        df = self.load_data(file_path)
        print(f"Loaded data with shape: {df.shape}")

        # Handle missing values
        df = self.handle_missing_values(df)
        print("Handled missing values")

        # Remove outliers for numerical columns
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_column and target_column in num_cols:
            num_cols.remove(target_column)
        if num_cols:
            df = self.remove_outliers(df, num_cols)
            print("Removed outliers")

        # Normalize numerical data
        if num_cols:
            df = self.normalize_data(df, num_cols)
            print("Normalized numerical data")

        # Encode categorical data
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if target_column and target_column in cat_cols:
            cat_cols.remove(target_column)
        if cat_cols:
            df = self.encode_categorical(df, cat_cols)
            print("Encoded categorical data")

        # Feature engineering
        df = self.feature_engineering(df)
        print("Performed feature engineering")

        # Split data if target column is specified
        if target_column and target_column in df.columns:
            X = df.drop(target_column, axis=1)
            y = df[target_column]
            X_train, X_test, y_train, y_test = self.split_data(X, y)
            return X_train, X_test, y_train, y_test
        else:
            return df


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Data Preprocessing Tool")
    parser.add_argument("file_path", help="Path to the data file")
    parser.add_argument("--target", help="Target column name for supervised learning")
    parser.add_argument("--output", help="Output file path for processed data")

    args = parser.parse_args()

    preprocessor = DataPreprocessor()

    try:
        if args.target:
            X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(args.file_path, args.target)
            print("Data preprocessing completed!")
            print(f"Training set shape: {X_train.shape}")
            print(f"Testing set shape: {X_test.shape}")

            if args.output:
                # Save processed data
                train_data = pd.concat([X_train, y_train], axis=1)
                test_data = pd.concat([X_test, y_test], axis=1)
                train_data.to_csv(f"{args.output}_train.csv", index=False)
                test_data.to_csv(f"{args.output}_test.csv", index=False)
                print(f"Processed data saved to {args.output}_train.csv and {args.output}_test.csv")
        else:
            processed_data = preprocessor.preprocess_pipeline(args.file_path)
            print("Data preprocessing completed!")
            print(f"Processed data shape: {processed_data.shape}")

            if args.output:
                processed_data.to_csv(args.output, index=False)
                print(f"Processed data saved to {args.output}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()