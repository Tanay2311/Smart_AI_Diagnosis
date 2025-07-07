import pandas as pd
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

nltk.download('punkt')
smoothie = SmoothingFunction().method4

# Load CSV
df = pd.read_csv("bleu_test_data_fixed.csv")  

bleu_scores = []

for i, row in df.iterrows():
    expected = [nltk.word_tokenize(row['Expected_Diagnosis_1'].lower()),
                nltk.word_tokenize(row['Expected_Diagnosis_2'].lower())]
    
    generated = nltk.word_tokenize(str(row['LLM_Generated_Diagnosis']).lower())

    # Calculate BLEU score
    score = sentence_bleu(expected, generated, smoothing_function=smoothie)
    bleu_scores.append(score)

df["BLEU_Score"] = bleu_scores

# Save with BLEU column
df.to_csv("diagnosis_eval_with_bleu.csv", index=False)
print("✅ BLEU evaluation complete. File saved as diagnosis_eval_with_bleu.csv")
print(f"Average BLEU Score: {sum(bleu_scores)/len(bleu_scores):.4f}")
