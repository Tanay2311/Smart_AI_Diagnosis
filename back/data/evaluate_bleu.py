import pandas as pd
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# Load CSV
df = pd.read_csv("bleu_test_data_with_predictions.csv")

# Fill NA with empty strings
df["LLM_Generated_Diagnosis"] = df["LLM_Generated_Diagnosis"].fillna("")
df["Expected_Diagnosis_1"] = df["Expected_Diagnosis_1"].fillna("")
df["Expected_Diagnosis_2"] = df["Expected_Diagnosis_2"].fillna("")

# Prepare BLEU evaluation
smoothie = SmoothingFunction().method4
bleu_scores = []

for idx, row in df.iterrows():
    references = []
    if row["Expected_Diagnosis_1"]:
        references.append(row["Expected_Diagnosis_1"].lower().split())
    if row["Expected_Diagnosis_2"]:
        references.append(row["Expected_Diagnosis_2"].lower().split())

    candidate = row["LLM_Generated_Diagnosis"].lower().split()

    if references and candidate:
        score = sentence_bleu(references, candidate, smoothing_function=smoothie)
    else:
        score = 0.0
    bleu_scores.append(score)

# Print final average score
average_bleu = sum(bleu_scores) / len(bleu_scores)
print(f"✅ Average BLEU Score: {average_bleu:.4f}")
