# feature_importance.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import os

# Files expected in repo root
FILES = [
    "data/features/features_normal.csv",
    "data/features/features_timing_attack.csv",
    "data/features/features_replay_attack.csv"
]

# load & concat
dfs = []
for f in FILES:
    if not os.path.exists(f):
        raise SystemExit(f"Missing file: {f}")
    dfs.append(pd.read_csv(f))
df = pd.concat(dfs, ignore_index=True)

X = df.drop(columns=["label"])
y = df["label"]

# train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# train
model = RandomForestClassifier(n_estimators=300, random_state=42)
model.fit(X_train, y_train)

# feature importances
importances = model.feature_importances_
feat_names = X.columns.tolist()
fi = pd.DataFrame({"feature": feat_names, "importance": importances})
fi = fi.sort_values("importance", ascending=False).reset_index(drop=True)
print("\nFeature importances (top):")
print(fi.head(20).to_string(index=False))

# save csv
fi.to_csv("/data/features/feature_importances.csv", index=False)
print("\nSaved feature_importances.csv")

# plot and save figure
plt.figure(figsize=(8, max(4, 0.3 * len(fi))))
plt.barh(fi["feature"][::-1], fi["importance"][::-1])
plt.xlabel("Importance")
plt.title("Feature importances (RandomForest)")
plt.tight_layout()
plt.savefig("feature_importances.png", dpi=150)
print("Saved feature_importances.png")

# Evaluate and show classification report too
y_pred = model.predict(X_test)
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))