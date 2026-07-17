import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from utils.preprocess import *
from utils.feature_engineering import *
from utils.model_training import *
from utils.evaluation import *

print("=" * 60)
print(" ICU Mortality Prediction System ")
print("=" * 60)

# -----------------------------------
# Load Dataset
# -----------------------------------
df = load_data()

# -----------------------------------
# Clean Dataset
# -----------------------------------
df = clean_data(df)

# -----------------------------------
# Encode Categorical Features
# -----------------------------------
df = encode_features(df)

# -----------------------------------
# Feature Engineering
# -----------------------------------
df = create_features(df)
import joblib

# Save Feature Order
feature_columns = df.drop("mortality", axis=1).columns.tolist()

joblib.dump(
    feature_columns,
    "models/feature_columns.pkl"
)

print("Feature Order Saved Successfully")

# -----------------------------------
# Split Dataset
# -----------------------------------
X_train, X_test, y_train, y_test = split_dataset(df)

print("\nTraining Models...\n")

# -----------------------------------
# Build Models
# -----------------------------------
models = get_models()

# -----------------------------------
# Train Models
# -----------------------------------
trained_models = train_models(
    models,
    X_train,
    y_train
)

# -----------------------------------
# Save Models
# -----------------------------------
save_models(trained_models)

# ---------------------------------------
# Save Only XGBoost Model
# ---------------------------------------

xgb_model = trained_models["XGBoost"]

joblib.dump(
    xgb_model,
    "models/xgb_model.pkl"
)

print("\n")
print("=" * 60)
print("XGBOOST MODEL RESULTS")
print("=" * 60)

y_pred = xgb_model.predict(X_test)
y_prob = xgb_model.predict_proba(X_test)[:, 1]

print("Accuracy :", round(accuracy_score(y_test, y_pred), 4))
print("Precision:", round(precision_score(y_test, y_pred), 4))
print("Recall   :", round(recall_score(y_test, y_pred), 4))
print("F1 Score :", round(f1_score(y_test, y_pred), 4))
print("ROC AUC  :", round(roc_auc_score(y_test, y_prob), 4))

print("\nXGBoost Model Saved Successfully")
# -----------------------------------
# Evaluate Models
# -----------------------------------
scores = evaluate_models(
    trained_models,
    X_test,
    y_test
)

print("\n================ MODEL COMPARISON ================\n")

for model, score in scores.items():
    print(f"{model} : ROC AUC = {score:.4f}")

print("\nTraining Completed Successfully!")