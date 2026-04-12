import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

df = pd.read_csv('hiring_data.csv')
target = 'hired'
X = df.drop(columns=[target])
y = df[target]

numerical = X.select_dtypes(include=['int64','float64']).columns.tolist()
categorical = X.select_dtypes(include=['object']).columns.tolist()

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numerical),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical)
])
X_processed = preprocessor.fit_transform(X)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_processed, y)

joblib.dump(model, 'hiring_model.pkl')
joblib.dump(preprocessor, 'hiring_preprocessor.pkl')
print("Saved hiring_model.pkl and hiring_preprocessor.pkl")