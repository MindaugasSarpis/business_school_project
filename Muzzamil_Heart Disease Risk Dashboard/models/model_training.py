import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load the processed data
df = pd.read_csv('data/processed/heart_risk_processed.csv')

# Define all features used during training
all_features = [
    'Age', 'Gender', 'High_BP', 'High_Cholesterol', 'Diabetes', 'Smoking',
    'Obesity', 'Sedentary_Lifestyle', 'Family_History', 'Chronic_Stress',
    'Chest_Pain', 'Cold_Sweats_Nausea', 'Dizziness', 'Fatigue', 'Pain_Arms_Jaw_Back',
    'Palpitations', 'Shortness_of_Breath', 'Swelling'
]

# Ensure all features are present in the dataframe
for feature in all_features:
    if feature not in df.columns:
        df[feature] = 0

# Drop non-feature columns if present
drop_cols = ['Heart_Risk', 'AgeGroup'] if 'AgeGroup' in df.columns else ['Heart_Risk']
X = df.drop(columns=drop_cols)
y = df['Heart_Risk']

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train Random Forest model
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Evaluate the model
y_pred = rf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save the trained model
joblib.dump(rf, 'models/heart_risk_rf_model.joblib')
print("Model saved to models/heart_risk_rf_model.joblib")