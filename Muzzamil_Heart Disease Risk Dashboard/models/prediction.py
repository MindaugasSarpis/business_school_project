import pandas as pd
import joblib

# Load the trained model
model = joblib.load('models/heart_risk_rf_model.joblib')

def predict_heart_risk(age, gender, risk_factors):
    # Define all features used during training
    all_features = [
        'Age', 'Gender', 'High_BP', 'High_Cholesterol', 'Diabetes', 'Smoking',
        'Obesity', 'Sedentary_Lifestyle', 'Family_History', 'Chronic_Stress',
        'Chest_Pain', 'Cold_Sweats_Nausea', 'Dizziness', 'Fatigue', 'Pain_Arms_Jaw_Back',
        'Palpitations', 'Shortness_of_Breath', 'Swelling'
    ]

    # Prepare input data for prediction
    input_data = pd.DataFrame({
        'Age': [age],
        'Gender': [1 if gender == "Male" else 0],
        **{factor: [1 if risk_factors.get(factor, False) else 0] for factor in all_features if factor not in ['Age', 'Gender']}
    }, columns=all_features)  # Ensure the order of columns matches the training data

    # Debug: Print input data to verify structure
    print(input_data)

    # Make prediction
    prediction = model.predict(input_data)[0]
    risk_label = "At Risk" if prediction == 1 else "No Risk"
    
    return risk_label