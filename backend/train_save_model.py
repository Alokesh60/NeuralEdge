"""
train_save_model.py
Train a model on a dataset and save both the model and its fitted preprocessor.
These files can later be used in pretrained mode via /audit/tabular/flexible.
"""

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
import os

# ======================== CONFIGURATION ========================
# Change these values as needed
DATASET_PATH = "adult_with_header.csv"   # Training CSV (must have header)
TARGET_COLUMN = "income"                 # Name of the target column
SENSITIVE_COLUMNS = ["sex"]              # Not used in preprocessor, just for reference
MODEL_TYPE = "randomforest"              # "logistic" or "randomforest"
OUTPUT_MODEL = "my_pretrained_model.pkl"
OUTPUT_PREPROCESSOR = "my_pretrained_preprocessor.pkl"
# ================================================================

def ensure_header_dataset():
    """If adult_with_header.csv doesn't exist, create it from adult.data."""
    if os.path.exists(DATASET_PATH):
        print(f"Dataset {DATASET_PATH} already exists.")
        return DATASET_PATH
    
    raw_file = "adult.data"
    if not os.path.exists(raw_file):
        import urllib.request
        print("Downloading adult.data...")
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
        urllib.request.urlretrieve(url, raw_file)
        print("Download complete.")
    
    print("Converting adult.data to adult_with_header.csv...")
    cols = [
        'age', 'workclass', 'fnlwgt', 'education', 'education-num',
        'marital-status', 'occupation', 'relationship', 'race', 'sex',
        'capital-gain', 'capital-loss', 'hours-per-week',
        'native-country', 'income'
    ]
    df = pd.read_csv(raw_file, names=cols, na_values=' ?', skipinitialspace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['income'] = (df['income'].str.strip() == '>50K').astype(int)
    df.to_csv(DATASET_PATH, index=False)
    print(f"Saved {DATASET_PATH} with {len(df)} rows.")
    return DATASET_PATH

def main():
    # Ensure we have a dataset with header
    csv_path = ensure_header_dataset()
    
    # Load data
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")
    
    # Prepare features and target
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]
    
    # Convert target to binary if needed (already binary, but safe)
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
    
    # Identify numerical and categorical columns (excluding target and sensitive)
    numerical = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Optionally remove sensitive columns from features (if you want a fairer model)
    # For demonstration, we keep them (biased model). Uncomment below to remove them.
    # for sens in SENSITIVE_COLUMNS:
    #     if sens in numerical:
    #         numerical.remove(sens)
    #     if sens in categorical:
    #         categorical.remove(sens)
    
    print("Numerical features:", numerical)
    print("Categorical features:", categorical)
    
    # Create and fit preprocessor
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numerical),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical)
    ])
    X_processed = preprocessor.fit_transform(X)
    print(f"Preprocessor fitted. Transformed shape: {X_processed.shape}")
    
    # Train model
    if MODEL_TYPE.lower() == "logistic":
        model = LogisticRegression(max_iter=1000, random_state=42)
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    model.fit(X_processed, y)
    print(f"Model {MODEL_TYPE} trained.")
    
    # Save both
    joblib.dump(model, OUTPUT_MODEL)
    joblib.dump(preprocessor, OUTPUT_PREPROCESSOR)
    print(f"Saved model to {OUTPUT_MODEL}")
    print(f"Saved preprocessor to {OUTPUT_PREPROCESSOR}")
    
    # Optional: evaluate on a small hold-out (just for info)
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)
    acc = model.score(X_test, y_test)
    print(f"Model accuracy on hold-out: {acc:.4f}")

if __name__ == "__main__":
    main()