import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
from itertools import chain

# Load the original file
df = pd.read_csv("medical_knowledge.csv")

# Drop rows with missing essential fields
df_cleaned = df.dropna(subset=["Disease", "Symptoms", "Description"])

# Drop duplicate rows
df_cleaned = df_cleaned.drop_duplicates()

# Strip whitespace and lower case for uniformity
def clean_text(text):
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s,]', '', text)  # Remove special characters except commas (which may separate symptoms)
    return text

for col in ["Disease", "Symptoms", "Description"]:
    df_cleaned[col] = df_cleaned[col].astype(str).apply(clean_text)

# Remove entries with very short or meaningless descriptions
df_cleaned = df_cleaned[df_cleaned["Description"].str.len() > 20]

# Save cleaned data
df_cleaned.to_csv("medical_knowledge_clean.csv", index=False)
print("✅ Cleaned CSV saved as 'medical_knowledge_clean.csv'")

# -------------------------------
# 🔍 Basic Textual Analysis
# -------------------------------


# Split symptoms and explode into individual rows
df_symptoms = df_cleaned.copy()
df_symptoms['Symptoms'] = df_symptoms['Symptoms'].str.split(',')
df_symptoms = df_symptoms.explode('Symptoms')
df_symptoms['Symptoms'] = df_symptoms['Symptoms'].str.strip()

# Count frequency of each symptom
symptom_counts = df_symptoms['Symptoms'].value_counts().nlargest(15)

# 📊 Bar plot: Top 15 symptoms by frequency
plt.figure(figsize=(12, 6))
symptom_counts.plot(kind='bar', color='coral')
plt.title("Top 15 Most Common Symptoms")
plt.xlabel("Symptom")
plt.ylabel("Frequency")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🧩 Mapping: How many unique diseases each symptom is associated with
symptom_disease_map = df_symptoms.groupby('Symptoms')['Disease'].nunique()
top_symptoms_disease_map = symptom_disease_map.loc[symptom_counts.index]

# Bar plot: Symptom vs # of unique diseases
plt.figure(figsize=(12, 6))
top_symptoms_disease_map.plot(kind='bar', color='slateblue')
plt.title("Top 15 Symptoms vs Number of Associated Diseases")
plt.xlabel("Symptom")
plt.ylabel("Number of Unique Diseases")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# Number of symptoms per row
df_cleaned['Symptom_Count'] = df_cleaned['Symptoms'].apply(lambda x: len(x.split(',')))

# Symptom count distribution
plt.figure(figsize=(10, 5))
sns.histplot(df_cleaned['Symptom_Count'], bins=range(1, df_cleaned['Symptom_Count'].max()+2), kde=False, color='orange')
plt.title("Distribution of Number of Symptoms per Disease")
plt.xlabel("Number of Symptoms")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()

# Description length distribution
df_cleaned['Description_Length'] = df_cleaned['Description'].apply(len)

plt.figure(figsize=(10, 5))
sns.histplot(df_cleaned['Description_Length'], bins=30, color='green')
plt.title("Distribution of Description Lengths")
plt.xlabel("Description Length (characters)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()
