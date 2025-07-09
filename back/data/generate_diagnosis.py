import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load the data with predictions
df = pd.read_csv("bleu_test_data_with_predictions.csv")

# Load a sentence transformer model (compact and effective)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Prepare expected vs generated diagnosis strings
expected = df["Expected_Diagnosis_1"].fillna("") + "; " + df["Expected_Diagnosis_2"].fillna("")
generated = df["LLM_Generated_Diagnosis"].fillna("")

# Embed all sentences
expected_embeddings = model.encode(expected.tolist(), convert_to_tensor=True)
generated_embeddings = model.encode(generated.tolist(), convert_to_tensor=True)

# Compute cosine similarities
cosine_scores = util.cos_sim(expected_embeddings, generated_embeddings).diagonal()

# Save scores to dataframe
df["Semantic_Similarity"] = cosine_scores.cpu().numpy()

# Summary stats
avg_score = cosine_scores.mean().item()
threshold_0_7 = (cosine_scores > 0.7).float().mean().item()
threshold_0_5 = (cosine_scores > 0.5).float().mean().item()


print("📊 Semantic Evaluation Summary:")
print(f"✅ Average Cosine Similarity: {avg_score:.4f}")
print(f"🔼 % above 0.7 similarity: {threshold_0_7*100:.2f}%")
print(f"🔼 % above 0.5 similarity: {threshold_0_5*100:.2f}%")

# Optional: print bottom 5 worst cases
print("\n❌ Bottom 5 Lowest Similarity Cases:")
lowest = df.sort_values(by="Semantic_Similarity").head(5)
for i, row in lowest.iterrows():
    print(f"\nRow {i}:")
    print(f"Expected: {row['Expected_Diagnosis_1']}, {row['Expected_Diagnosis_2']}")
    print(f"Generated: {row['LLM_Generated_Diagnosis']}")
    print(f"Score: {row['Semantic_Similarity']:.4f}")

# Save updated CSV
df.to_csv("semantic_eval_results.csv", index=False)
print("\nSemantic similarity scores saved to 'semantic_eval_results.csv'")
