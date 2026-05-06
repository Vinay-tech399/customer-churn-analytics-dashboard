
import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, "data", "customer_churn_data.csv")
MODEL_PATH = os.path.join(ROOT, "models", "churn_model.joblib")
METRICS_PATH = os.path.join(ROOT, "models", "metrics.txt")

def main():
    df = pd.read_csv(DATA_PATH)
    y = (df["churn"] == "Yes").astype(int)
    X = df.drop(columns=["customer_id", "churn"])
    categorical = X.select_dtypes(include="object").columns.tolist()
    numeric = X.select_dtypes(exclude="object").columns.tolist()

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", StandardScaler(), numeric),
    ])

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=250, max_depth=10, min_samples_leaf=8, random_state=42, class_weight="balanced"),
    }

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    best_name, best_pipe, best_auc = None, None, -1
    report_lines=[]
    for name, model in models.items():
        pipe = Pipeline([("prep", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, proba)
        report_lines.append(f"MODEL: {name}
Accuracy: {accuracy_score(y_test, pred):.3f}
ROC AUC: {auc:.3f}
Confusion matrix:
{confusion_matrix(y_test, pred)}
{classification_report(y_test, pred)}
")
        if auc > best_auc:
            best_name, best_pipe, best_auc = name, pipe, auc

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(best_pipe, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        f.write("Best model: " + best_name + "

" + "
".join(report_lines))
    print(f"Saved best model: {best_name} with AUC={best_auc:.3f}")

if __name__ == "__main__":
    main()
