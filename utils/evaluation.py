import os
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    RocCurveDisplay
)


def evaluate_models(trained_models, X_test, y_test):

    os.makedirs("results", exist_ok=True)

    metrics_file = open("results/metrics.txt", "w")

    scores = {}

    for name, model in trained_models.items():

        print("=" * 60)
        print("Evaluating :", name)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:,1]

        acc = accuracy_score(y_test, y_pred)
        pre = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        scores[name] = auc

        metrics_file.write(f"\n{name}\n")
        metrics_file.write("-"*40 + "\n")
        metrics_file.write(f"Accuracy : {acc:.4f}\n")
        metrics_file.write(f"Precision: {pre:.4f}\n")
        metrics_file.write(f"Recall   : {rec:.4f}\n")
        metrics_file.write(f"F1 Score : {f1:.4f}\n")
        metrics_file.write(f"ROC AUC  : {auc:.4f}\n\n")

        print(f"Accuracy : {acc:.4f}")
        print(f"Precision: {pre:.4f}")
        print(f"Recall   : {rec:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print(f"ROC AUC  : {auc:.4f}")

        # ------------------------
        # Confusion Matrix
        # ------------------------

        disp = ConfusionMatrixDisplay(
            confusion_matrix(y_test, y_pred)
        )

        disp.plot()

        plt.title(name + " Confusion Matrix")

        plt.savefig(
            f"results/{name.lower().replace(' ','_')}_confusion_matrix.png"
        )

        plt.close()

        # ------------------------
        # ROC Curve
        # ------------------------

        RocCurveDisplay.from_predictions(
            y_test,
            y_prob
        )

        plt.title(name + " ROC Curve")

        plt.savefig(
            f"results/{name.lower().replace(' ','_')}_roc_curve.png"
        )

        plt.close()

    metrics_file.close()

    return scores