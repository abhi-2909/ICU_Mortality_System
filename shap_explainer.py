import joblib
import shap
import pandas as pd

# ----------------------------
# Load XGBoost Model
# ----------------------------
model = joblib.load("models/xgb_model.pkl")

# ----------------------------
# Load Feature Order
# ----------------------------
feature_columns = joblib.load(
    "models/feature_columns.pkl"
)

# ----------------------------
# Create SHAP Explainer
# ----------------------------
explainer = shap.TreeExplainer(model)


def explain_prediction(features):

    """
    Returns the top contributing features
    for a single prediction.
    """

    # Convert to DataFrame
    df = pd.DataFrame([features])

    # Match training feature order
    df = df[feature_columns]

    # Calculate SHAP values
    shap_values = explainer.shap_values(df)

    # Binary classification handling
    if isinstance(shap_values, list):
        values = shap_values[1][0]
    else:
        values = shap_values[0]

    explanation = []

    for feature, value in zip(feature_columns, values):

        explanation.append({

            "feature": feature,

            "impact": round(float(value), 4)

        })

    # Sort by absolute impact
    explanation.sort(
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    # Return top 5 features
    return explanation[:5]