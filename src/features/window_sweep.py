import subprocess
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

WINDOWS = [0.1, 0.2, 0.5]

PCAPS = {
    "normal": "data/pcaps/normal.pcapng",
    "timing_attack": "data/pcaps/timing_attack.pcapng",
    "replay_attack": "data/pcaps/replay_attack.pcapng",
    "command_injection": "data/pcaps/command_injection.pcapng",
}

results = []

for w in WINDOWS:
    print(f"\n=== Window = {w}s ===")

    # Regenerate features for each class
    for label, pcap in PCAPS.items():
        out_csv = f"data/features/features_{label}_w{w}.csv"
        cmd = [
            "python", "src/features/pcap_to_features.py",
            "--pcap", pcap,
            "--window", str(w),
            "--label", label,
            "--out", out_csv
        ]
        subprocess.check_call(cmd)

    # Load features and train model
    df = pd.concat([
        pd.read_csv(f"data/features/features_normal_w{w}.csv"),
        pd.read_csv(f"data/features/features_timing_attack_w{w}.csv"),
        pd.read_csv(f"data/features/features_replay_attack_w{w}.csv"),
        pd.read_csv(f"data/features/features_command_injection_w{w}.csv"),
    ], ignore_index=True)

    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    results.append({
        "window_s": w,
        "accuracy": acc,
        "macro_f1": macro_f1,
        "latency_estimate_s": w
    })

    print(f"accuracy={acc:.4f}  macro_f1={macro_f1:.4f}")

out = pd.DataFrame(results)
out.to_csv("data/features/window_sweep_results.csv", index=False)

print("\nSaved window_sweep_results.csv")
print(out.to_string(index=False))
