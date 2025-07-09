import pandas as pd
import time
from sklearn.metrics import precision_score, recall_score, f1_score
from diagnosis_assistant import extract_symptoms, follow_up_map
from rapidfuzz import fuzz
from collections import Counter

# Load test cases
df = pd.read_csv("ai_medical_assistant_test_cases.csv")

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
