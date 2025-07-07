import pandas as pd
import time
from sklearn.metrics import precision_score, recall_score, f1_score
from diagnosis_assistant import extract_symptoms, follow_up_map, rag_chain  
from rapidfuzz import fuzz


# Load test cases
df = pd.read_csv("ai_medical_assistant_test_cases.csv")

# Initialize logs
extracted_results = []
latency_logs = []
followup_accuracy = []

def normalize(sym_str):
    if pd.isna(sym_str):
        return []
    return sorted([s.strip().lower() for s in sym_str.split(",") if s.strip()])

# Evaluate each test case
for idx, row in df.iterrows():
    input_text = row["Input"]
    expected_symptoms = normalize(str(row["Expected_Symptoms"]))

    start = time.time()
    extracted = extract_symptoms(input_text)
    end = time.time()

    latency_logs.append(round(end - start, 2))
    extracted_results.append(extracted)

    # Calculate follow-up coverage
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

# Symptom Extraction Evaluation
all_expected = []
all_predicted = []

for idx, row in df.iterrows():
    expected = normalize(row["Expected_Symptoms"])
    predicted = extracted_results[idx]

    for sym in predicted:
        all_predicted.append(1)
        all_expected.append(1 if sym in expected else 0)

# Metrics
precision = precision_score(all_expected, all_predicted)
recall = recall_score(all_expected, all_predicted)
f1 = f1_score(all_expected, all_predicted)

# Report
print("\n==== 🧠 Symptom Extraction Metrics ====")
print(f"Precision: {precision:.2f}")
print(f"Recall:    {recall:.2f}")
print(f"F1 Score:  {f1:.2f}")

print("\n==== ⏱ Latency per Sample (seconds) ====")
for i, t in enumerate(latency_logs):
    print(f"Case {i+1}: {t} sec")

print("\n==== 🔍 Follow-up Match Accuracy ====")
for r in followup_accuracy:
    print(f"- {r['Input'][:40]}... | Matched {r['Matched_Followups']}/{r['Expected_Followups']} follow-ups")

from collections import Counter

tp_total, fp_total, fn_total = 0, 0, 0
symptom_stats = []

for idx, row in df.iterrows():
    expected = set(normalize(row["Expected_Symptoms"]))
    predicted = set(extracted_results[idx])

    true_positives = expected & predicted
    false_positives = predicted - expected
    false_negatives = expected - predicted

    tp, fp, fn = len(true_positives), len(false_positives), len(false_negatives)
    tp_total += tp
    fp_total += fp
    fn_total += fn

    symptom_stats.append({
        "Input": row["Input"][:40] + "...",
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "Extracted": list(predicted),
        "Expected": list(expected)
    })

# Print detailed results
print("\n==== 🔬 Per-Sample Symptom Matching ====")
for s in symptom_stats:
    print(f"- {s['Input']} | TP: {s['TP']} | FP: {s['FP']} | FN: {s['FN']}")

# Overall metrics
prec = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0
rec = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0
f1_final = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0

print("\n==== 📊 Aggregate Symptom Metrics ====")
print(f"Total TP: {tp_total} | FP: {fp_total} | FN: {fn_total}")
print(f"Precision: {prec:.2f} | Recall: {rec:.2f} | F1 Score: {f1_final:.2f}")
