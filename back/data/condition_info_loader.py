# back/data/condition_info_loader.py

import os
import csv

# -------------------- Configs --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "medical_knowledge_clean.csv")

condition_database = {}

# -------------------- Load CSV --------------------
with open(DATA_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["Disease"].strip().lower()
        condition_database[name] = {
            "description": row.get("Description", "").strip(),
            "symptoms": [x.strip() for x in row.get("Symptoms", "").split(",") if x.strip()],
            "treatments": [x.strip() for x in row.get("Treatment", "").split(",") if x.strip()],
            "risks": [x.strip() for x in row.get("Risk_Factors", "").split(",") if x.strip()],
        }
