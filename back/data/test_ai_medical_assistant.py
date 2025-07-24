import pandas as pd
import time
from sklearn.metrics import precision_score, recall_score, f1_score
from diagnosis_assistant import extract_symptoms, follow_up_map
from rapidfuzz import fuzz
from collections import Counter

# Load test cases
df = pd.read_csv("testing_v2.csv")

# Helpers
def normalize(sym_str):
    if pd.isna(sym_str):
        return []
    return sorted([s.strip().lower() for s in sym_str.split(",") if s.strip()])

# Initialize logs
extracted_results = []
latency_logs = []
followup_accuracy = []
symptom_stats = []

all_expected = []
all_predicted = []

tp_total, fp_total, fn_total = 0, 0, 0

# Evaluation loop
for idx, row in df.iterrows():
    input_text = row["Input"]
    expected_symptoms = set(normalize(row["Expected_Symptoms"]))

    # --- Symptom Extraction ---
    start = time.time()
    extracted = set(extract_symptoms(input_text))
    end = time.time()

    extracted_results.append(list(extracted))
    latency_logs.append(round(end - start, 2))

    # --- Follow-up Evaluation ---
    actual_followups = []
    for sym in extracted:
        actual_followups.extend(follow_up_map.get(sym, []))

    expected_followups = row["Expected_FollowUps"].split(";") if pd.notna(row["Expected_FollowUps"]) else []
    matched = sum(
        1 for q in expected_followups
        if any(fuzz.partial_ratio(q.strip().lower(), a.lower()) >= 85 for a in actual_followups)
    )

    followup_accuracy.append({
        "Input": input_text,
        "Expected_Followups": len(expected_followups),
        "Matched_Followups": matched
    })

    # --- Symptom Matching ---
    true_positives = expected_symptoms & extracted
    false_positives = extracted - expected_symptoms
    false_negatives = expected_symptoms - extracted

    tp, fp, fn = len(true_positives), len(false_positives), len(false_negatives)
    tp_total += tp
    fp_total += fp
    fn_total += fn

    # For overall metrics
    all_symptoms = expected_symptoms | extracted
    for sym in all_symptoms:
        all_expected.append(1 if sym in expected_symptoms else 0)
        all_predicted.append(1 if sym in extracted else 0)

    symptom_stats.append({
        "Input": input_text[:40] + "...",
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "Extracted": list(extracted),
        "Expected": list(expected_symptoms)
    })

# === METRICS ===
prec = precision_score(all_expected, all_predicted)
rec = recall_score(all_expected, all_predicted)
f1 = f1_score(all_expected, all_predicted)

# === OUTPUT ===
print(f"\n📄 Evaluated {len(df)} test cases")

print("\n==== 🧠 Symptom Extraction Metrics ====")
print(f"Precision: {prec:.2f}")
print(f"Recall:    {rec:.2f}")
print(f"F1 Score:  {f1:.2f}")

print("\n==== ⏱ Latency per Sample (seconds) ====")
for i, t in enumerate(latency_logs):
    print(f"Case {i+1}: {t} sec")

print("\n==== 🔍 Follow-up Match Accuracy ====")
for r in followup_accuracy:
    print(f"- {r['Input'][:40]}... | Matched {r['Matched_Followups']}/{r['Expected_Followups']} follow-ups")

print("\n==== 🔬 Per-Sample Symptom Matching ====")
for s in symptom_stats:
    print(f"- {s['Input']} | TP: {s['TP']} | FP: {s['FP']} | FN: {s['FN']}")

print("\n==== 📊 Aggregate Symptom Metrics ====")
print(f"Total TP: {tp_total} | FP: {fp_total} | FN: {fn_total}")
print(f"Precision: {tp_total / (tp_total + fp_total):.2f} | Recall: {tp_total / (tp_total + fn_total):.2f} | F1 Score: {2 * tp_total / (2 * tp_total + fp_total + fn_total):.2f}")

# === FP / FN Analysis ===
fp_symptoms = [sym for stat in symptom_stats for sym in set(stat['Extracted']) - set(stat['Expected'])]
fn_symptoms = [sym for stat in symptom_stats for sym in set(stat['Expected']) - set(stat['Extracted'])]

print("\n🔁 Top False Positives:")
for sym, count in Counter(fp_symptoms).most_common(5):
    print(f"- {sym}: {count}")

print("\n❌ Top False Negatives:")
for sym, count in Counter(fn_symptoms).most_common(5):
    print(f"- {sym}: {count}")

# === Save Results ===
pd.DataFrame(symptom_stats).to_csv("symptom_eval_detailed.csv", index=False)
pd.DataFrame(followup_accuracy).to_csv("followup_eval.csv", index=False)

import matplotlib.pyplot as plt
import seaborn as sns

# Set seaborn style
sns.set(style="whitegrid")

# === 1. Bar Chart for Precision, Recall, F1 ===
# Shows the overall effectiveness of symptom extraction
plt.figure(figsize=(6, 4))
metrics = [prec, rec, f1]
labels = ["Precision", "Recall", "F1 Score"]
sns.barplot(x=labels, y=metrics, palette="Blues_d")
plt.title("Symptom Extraction Metrics")
plt.ylim(0, 1.05)
plt.ylabel("Score")
for i, val in enumerate(metrics):
    plt.text(i, val + 0.02, f"{val:.2f}", ha='center')
plt.tight_layout()
plt.savefig("symptom_metrics_bar_chart.png")
print("✅ Saved: symptom_metrics_bar_chart.png")
plt.show()

# === 2. Latency per Case ===
# Visualizes how long each test case took to process (for performance evaluation)
plt.figure(figsize=(10, 4))
sns.lineplot(x=list(range(1, len(latency_logs)+1)), y=latency_logs, marker="o", color="purple")
plt.title("Latency per Sample")
plt.xlabel("Test Case #")
plt.ylabel("Latency (seconds)")
plt.tight_layout()
plt.savefig("latency_per_case.png")
print("✅ Saved: latency_per_case.png")
plt.show()

# === 3. TP / FP / FN Bar Chart per Case ===
# Shows true positives, false positives, and false negatives for each input
df_stats = pd.DataFrame(symptom_stats)
plt.figure(figsize=(12, 6))
df_stats_melted = df_stats[["Input", "TP", "FP", "FN"]].melt(id_vars="Input", var_name="Metric", value_name="Count")
sns.barplot(data=df_stats_melted, x="Input", y="Count", hue="Metric")
plt.title("True Positives, False Positives, False Negatives per Case")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("tp_fp_fn_per_case.png")
print("✅ Saved: tp_fp_fn_per_case.png")
plt.show()

# === 4. Follow-up Match Ratio ===
# Measures how well follow-up questions were matched (value between 0 and 1)
df_followup = pd.DataFrame(followup_accuracy)
df_followup["Match_Ratio"] = df_followup["Matched_Followups"] / df_followup["Expected_Followups"].replace(0, 1)
plt.figure(figsize=(10, 4))
sns.barplot(x=list(range(1, len(df_followup)+1)), y="Match_Ratio", data=df_followup, color="green")
plt.title("Follow-up Match Accuracy per Case")
plt.xlabel("Test Case #")
plt.ylabel("Match Ratio")
plt.ylim(0, 1.05)
plt.tight_layout()
plt.savefig("followup_match_ratio.png")
print("✅ Saved: followup_match_ratio.png")
plt.show()

# === 5. Top 5 False Positives ===
# These are symptoms predicted but not expected – helps understand over-prediction
fp_df = pd.DataFrame(Counter(fp_symptoms).most_common(5), columns=["Symptom", "Count"])
plt.figure(figsize=(6, 4))
sns.barplot(data=fp_df, x="Symptom", y="Count", palette="Reds_r")
plt.title("Top 5 False Positives")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("top_false_positives.png")
print("✅ Saved: top_false_positives.png")
plt.show()

# === 6. Top 5 False Negatives ===
# These are symptoms that were expected but not predicted – helps identify blind spots
fn_df = pd.DataFrame(Counter(fn_symptoms).most_common(5), columns=["Symptom", "Count"])
plt.figure(figsize=(6, 4))
sns.barplot(data=fn_df, x="Symptom", y="Count", palette="Greens_r")
plt.title("Top 5 False Negatives")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("top_false_negatives.png")
print("✅ Saved: top_false_negatives.png")
plt.show()
    