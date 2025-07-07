import os
import re
import time
import warnings
import pandas as pd
import spacy
from rapidfuzz import process
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# -------------------- Load Environment --------------------
load_dotenv()
warnings.simplefilter(action='ignore', category=FutureWarning)

# -------------------- Configs --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "medical_knowledge_clean.csv")
SYMPTOM_QA_PATH = os.path.join(BASE_DIR, "symptom_follow_up_questions.csv")
PERSIST_DIR = os.path.join(BASE_DIR, "rag_index")
EMBED_MODEL = "all-MiniLM-L6-v2"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ Please set your GOOGLE_API_KEY environment variable in a .env file.")

# -------------------- Load spaCy NLP Model --------------------
print("🔁 Loading spaCy model...")
nlp = spacy.load("en_ner_bc5cdr_md")

print("📄 Reading medical dataset...")
df = pd.read_csv(DATA_PATH)

# -------------------- Symptom Vocabulary --------------------
def build_symptom_vocab(df):
    symptoms = set()
    for s in df["Symptoms"].dropna():
        symptoms.update([sym.strip().lower() for sym in s.split(",")])
    return sorted(symptoms)

symptom_vocab = build_symptom_vocab(df)

# -------------------- Synonym Map --------------------
synonym_map = {
    # General
    "tired": "fatigue", "exhausted": "fatigue", "worn out": "fatigue", "feeling weak": "fatigue",
    "burned out": "fatigue", "lethargic": "fatigue", "lack of energy": "fatigue", "groggy": "fatigue",

    # Vision
    "blurry vision": "blurred vision", "can't see clearly": "blurred vision", "vision problems": "blurred vision",
    "seeing spots": "blurred vision", "dim vision": "blurred vision", "vision fades": "blurred vision",

    # Headache/Nausea
    "head pain": "headache", "hurting head": "headache", "pounding head": "headache",
    "migraine": "headache", "aching head": "headache",
    "feel nauseous": "nausea", "sick to stomach": "nausea", "want to throw up": "nausea",
    "puke": "nausea", "vomit": "nausea", "queasy": "nausea", "throwing up": "nausea",
    "retching": "nausea", "green around the gills": "nausea", "turned stomach": "nausea",

    # Fever
    "feverish": "fever", "hot body": "fever", "high temperature": "fever",
    "chills": "fever", "burning up": "fever", "hot flush": "fever", "temperature": "fever",

    # Chest
    "chest tightness": "chest pain", "pressure in chest": "chest pain", "chest discomfort": "chest pain",
    "burning in chest": "chest pain", "tight chest": "chest pain", "squeezing chest": "chest pain",
    "pain in chest when breathing": "chest pain",

    # Cold symptoms
    "runny nose": "rhinorrhea", "stuffy nose": "nasal congestion", "sneezing": "rhinorrhea",
    "coughing": "cough", "sniffles": "rhinorrhea", "drippy nose": "rhinorrhea",
    "phlegm": "cough", "sore throat": "throat pain",

    # Skin
    "skin bumps": "rash", "itchy skin": "rash", "red spots": "rash", "skin irritation": "rash",
    "redness on skin": "rash", "itchy spots": "rash", "hives": "rash",

    # Breathing
    "short of breath": "shortness of breath", "can't catch breath": "shortness of breath",
    "wheezing": "shortness of breath",

    # Others
    "sweats": "sweating", "shaky": "tremors","feeling dizzy": "dizziness", "feel dizzy": "dizziness", "skipped meals": "hypoglycemia",
    "skipping meals": "hypoglycemia", "light sensitivity": "photophobia",
    "light flashes": "photophobia", "disoriented": "confusion", "mental fog": "confusion",
    "loss of appetite": "anorexia", "can’t eat": "anorexia",
    "fainting": "syncope", "passed out": "syncope",

    # Heat-related
    "overheated": "heat exhaustion", "heatstroke": "heat exhaustion", "sun exposure": "heat exhaustion",
}

modifiers = [
    "constant", "throbbing", "sharp", "mild", "severe", "intermittent",
    "on and off", "persistent", "sudden", "gradual", "spinning", "dull"
]

# -------------------- Symptom Extraction --------------------
def extract_symptoms(text, threshold=92):
    text_lower = text.lower()
    doc = nlp(text)
    ner_extracted = [ent.text.lower() for ent in doc.ents if ent.label_ == "DISEASE"]

    synonyms_found = [synonym_map[key] for key in synonym_map if key in text_lower]
    keyword_matched = [sym for sym in symptom_vocab if re.search(rf'\b{re.escape(sym)}\b', text_lower)]

    pattern_based = [
        sym for mod in modifiers for sym in symptom_vocab
        if mod in text_lower and sym in text_lower
    ]

    combined = list(set(ner_extracted + synonyms_found + keyword_matched + pattern_based))
    final_matches = set()

    for s in combined:
        result = process.extractOne(s, symptom_vocab, score_cutoff=threshold)
        if result:
            final_matches.add(result[0])

    if not final_matches:
        fallback = process.extractOne(text_lower, symptom_vocab, score_cutoff=threshold - 7)
        if fallback:
            final_matches.add(fallback[0])

    return sorted(final_matches)

# -------------------- Follow-Up Questions --------------------
print("📥 Loading follow-up question map...")
follow_up_df = pd.read_csv(SYMPTOM_QA_PATH)
follow_up_map = {
    row["Symptom"].strip().lower(): [
        row["Follow_Up_1"], row["Follow_Up_2"], row["Follow_Up_3"], row["Follow_Up_4"]
    ]
    for _, row in follow_up_df.iterrows()
}

# -------------------- Vector Store Setup --------------------
print("🧠 Setting up vector index...")
embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

if os.path.exists(PERSIST_DIR):
    vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding)
else:
    print("📌 Creating new vector index...")
    loader = CSVLoader(file_path=DATA_PATH)
    docs = loader.load()
    vectordb = Chroma.from_documents(docs, embedding=embedding, persist_directory=PERSIST_DIR)

retriever = vectordb.as_retriever()

# -------------------- Gemini LLM Setup --------------------
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-pro", google_api_key=GOOGLE_API_KEY)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

rag_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    verbose=False
)

# -------------------- Response Optimizer --------------------
def summarize_response(response, max_lines=10):
    lines = response.strip().split("\n")
    summary = []

    for line in lines:
        line = line.strip()
        if line and not line.lower().startswith("please"):
            summary.append(line)
        if len(summary) >= max_lines:
            break

    summary.append("It's best to consult a healthcare provider for a clear diagnosis.")
    return "\n".join(summary)


# -------------------- Diagnosis Generator --------------------
def generate_diagnosis(symptoms, followup_answers, extra_input=""):
    all_answers = []
    for answers in followup_answers.values():
        all_answers.extend(answers)
    if extra_input:
        all_answers.append(f"Extra input: {extra_input}")

    final_context = ". ".join(all_answers)
    full_symptoms = ", ".join(symptoms)

    query = (
    f"Symptoms: {full_symptoms}. Context: {final_context}. "
    f"List exactly two possible medical conditions that could explain the symptoms. "
    f"Respond in this format:\n"
    f"1. Condition Name: ...\nReason: ...\n\n"
    f"2. Condition Name: ...\nReason: ..."
)


    result = rag_chain.invoke({"question": query})
    return summarize_response(result["answer"])

# -------------------- CLI Interactive Mode --------------------
def main():
    print("\n🩺 AI Medical Assistant (Gemini 2.5 Pro) is ready.")
    print("Describe your symptoms (type 'exit' to quit).\n")

    user_input = input("You: ").strip()
    if not user_input or user_input.lower() in ["exit", "quit"]:
        print("Goodbye.")
        return

    symptoms = extract_symptoms(user_input)
    if not symptoms:
        print("⚠️ Couldn't extract symptoms. Try rephrasing.")
        return

    print(f"✅ Extracted symptoms: {', '.join(symptoms)}")
    followup_answers = {}

    for symptom in symptoms:
        questions = follow_up_map.get(symptom, [])
        answers = []
        for i, q in enumerate(questions):
            print(f"\n🔍 Follow-up Q{i+1} for '{symptom}': {q}")
            ans = input("You: ").strip()
            answers.append(f"{q} -> {ans}")
        followup_answers[symptom] = answers

    extra = input("\n📝 Anything else you'd like to mention? ").strip()

    print("\n💬 Generating diagnosis, please wait...\n")
    start = time.time()
    diagnosis = generate_diagnosis(symptoms, followup_answers, extra)
    end = time.time()

    print(f"\n🧠 DocBot (⏱ {round(end - start, 2)} sec):\n" + "-"*50)
    print(diagnosis)
    print("-"*50)

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    main()
