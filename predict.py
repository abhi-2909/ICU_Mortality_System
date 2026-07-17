import joblib
import pandas as pd
from shap_explainer import explain_prediction

# ----------------------------
# Load Models
# ----------------------------

model = joblib.load("models/xgb_model.pkl")

feature_columns = joblib.load(
    "models/feature_columns.pkl"
)

gender_encoder = joblib.load(
    "models/gender_encoder.pkl"
)


def predict_patient(features):

    # ----------------------------
    # Encode Gender
    # ----------------------------
    features["gender"] = gender_encoder.transform(
        [features["gender"]]
    )[0]

    # ----------------------------
    # Feature Engineering
    # ----------------------------
    features["map"] = (
        features["systolic_bp"] +
        2 * features["diastolic_bp"]
    ) / 3

    features["pulse_pressure"] = (
        features["systolic_bp"] -
        features["diastolic_bp"]
    )

    features["shock_index"] = (
        features["heart_rate"] /
        features["systolic_bp"]
    )

    features["bun_creatinine_ratio"] = (
        features["bun"] /
        (features["creatinine"] + 0.01)
    )

    features["oxygen_deficit"] = (
        100 -
        features["spo2"]
    )

    features["elderly"] = int(
        features["age"] >= 65
    )

    # ----------------------------
    # Create DataFrame
    # ----------------------------
    df = pd.DataFrame([features])

    df = df[feature_columns]

    # ----------------------------
    # Prediction
    # ----------------------------
    probability = model.predict_proba(df)[0][1]

    prediction = model.predict(df)[0]

    # ----------------------------
    # Risk Level
    # ----------------------------
    if probability < 0.30:

        risk = "LOW"

    elif probability < 0.70:

        risk = "MEDIUM"

    else:

        risk = "HIGH"

    # ----------------------------
    # Recommendation
    # ----------------------------
    if risk == "LOW":

        recommendation = """
Continue routine ICU monitoring.
Maintain current treatment plan.
"""

    elif risk == "MEDIUM":

        recommendation = """
Increase monitoring frequency.
Repeat laboratory investigations.
Review patient after 6 hours.
"""

    else:

        recommendation = """
Immediate ICU intervention required.
Review ventilator support.
Monitor lactate.
Consult senior intensivist.
"""

    # ----------------------------
    # SHAP Explanation
    # ----------------------------
    shap_result = explain_prediction(features)

    # ----------------------------
    # Return Result
    # ----------------------------
    return {

        "prediction": int(prediction),

        "probability": round(
            probability * 100,
            2
        ),

        "confidence": round(
            max(model.predict_proba(df)[0]) * 100,
            2
        ),

        "risk": risk,

        "recommendation": recommendation,

        "shap": shap_result

    }