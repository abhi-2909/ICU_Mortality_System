import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import StackingClassifier

from sklearn.linear_model import LogisticRegression

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier


# --------------------------------------------------
# Build All Base Models
# --------------------------------------------------

def get_models():

    models = {}

    models["Random Forest"] = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )

    models["Extra Trees"] = ExtraTreesClassifier(
        n_estimators=300,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )

    models["XGBoost"] = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
        eval_metric="logloss"
    )

    models["LightGBM"] = LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )

    models["CatBoost"] = CatBoostClassifier(
        iterations=300,
        learning_rate=0.05,
        depth=6,
        verbose=False,
        random_seed=42
    )

    return models


# --------------------------------------------------
# Train Every Model
# --------------------------------------------------

def train_models(models, X_train, y_train):

    trained_models = {}

    for name, model in models.items():

        print("=" * 60)
        print("Training :", name)

        model.fit(X_train, y_train)

        trained_models[name] = model

        print(name, "Completed")

    return trained_models


# --------------------------------------------------
# Build Stacking Model
# --------------------------------------------------

def build_stacking(trained_models):

    estimators = [

        ("rf", trained_models["Random Forest"]),
        ("et", trained_models["Extra Trees"]),
        ("xgb", trained_models["XGBoost"]),
        ("lgbm", trained_models["LightGBM"]),
        ("cat", trained_models["CatBoost"])

    ]

    stacking = StackingClassifier(

        estimators=estimators,

        final_estimator=LogisticRegression(),

        n_jobs=-1

    )

    return stacking


# --------------------------------------------------
# Save Models
# --------------------------------------------------

def save_models(trained_models):

    print("\nSaving Models...\n")

    for name, model in trained_models.items():

        filename = (
            "models/" +
            name.lower().replace(" ", "_") +
            "_model.pkl"
        )

        joblib.dump(model, filename)

        print(filename)

    print("\nAll Models Saved Successfully")
    # --------------------------------------------------
# Train Stacking Ensemble
# --------------------------------------------------

def train_stacking_model(stacking_model, X_train, y_train):

    print("\n" + "=" * 60)
    print("Training Stacking Ensemble")
    print("=" * 60)

    stacking_model.fit(X_train, y_train)

    print("Stacking Ensemble Training Completed")

    return stacking_model