import os
import re
import time
from typing import List
import warnings
import pandas as pd
import spacy
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# -------------------- Load Environment --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)
warnings.simplefilter(action='ignore', category=FutureWarning)

# -------------------- Configs --------------------
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
# REVISED synonym_map

synonym_map = {
    # ==================== General ====================
    "tired": "fatigue",
    "exhausted": "fatigue",
    "worn out": "fatigue",
    "lethargic": "fatigue",
    "lack of energy": "fatigue",
    "feeling weak": "fatigue", # Mapped to fatigue for general weakness
    "fatigued": "fatigue",
    "tiredness": "fatigue",
    
    # ==================== Vision ====================
    "blurry vision": "blurred vision",
    "can't see clearly": "blurred vision",
    "dim vision": "blurred vision",
    "spots in vision": "floaters", # REFINED: 'floaters' is a more specific and useful term
    "seeing spots": "floaters",
    "floaters": "floaters",
    "flashes of light": "photopsia",
    "seeing double": "diplopia",
    "double vision": "diplopia",
    "crossed eyes": "strabismus",
    "sensitive to light": "photophobia",
    "light sensitivity": "photophobia",

    # ==================== Headache / Nausea ====================
    "head pain": "headache",
    "pounding head": "headache",
    "aching head": "headache",
    "migraine": "headache", # Mapping a specific type to the general symptom
    "feel nauseous": "nausea",
    "queasy": "nausea",
    "sick to stomach": "nausea",
    "want to throw up": "nausea",
    "puke": "nausea",
    "vomit": "vomiting", # REFINED: Separated vomiting from nausea
    "throwing up": "vomiting",
    
    # ==================== Fever / Chills ====================
    "feverish": "fever",
    "high temperature": "fever",
    "temperature": "fever",
    "chills": "chills", # REFINED: 'chills' is a distinct symptom from fever

    # ==================== Chest ====================
    "chest tightness": "chest pain",
    "chest discomfort": "chest pain",
    "pressure in chest": "chest pain",
    "squeezing chest": "chest pain",
    "heart racing": "palpitations",
    "pounding heart": "palpitations",
    "heart fluttering": "palpitations",

    # ==================== Cold / Respiratory ====================
    "sneezing": "sneezing",
    "runny nose": "runny nose",
    "sniffles": "runny nose",
    "drippy nose": "runny nose",
    "stuffy nose": "nasal congestion",
    "congested": "nasal congestion",
    "sore throat": "sore throat", # CHANGED: Standardized to 'sore throat'
    "scratchy throat": "sore throat",
    "throat pain": "sore throat",
    "hoarse voice": "hoarseness",
    "hoarseness": "hoarseness",
    "coughing": "cough",
    "cough": "cough",
    "phlegm": "sputum", # REFINED: Standardized to 'sputum'
    "mucus": "sputum",
    "green mucus": "sputum",
    
    # ==================== Skin ====================
    "red spots": "rash",
    "itchy skin": "itching", # REFINED: Separated itching from rash
    "itching": "itching",
    "hives": "rash",
    "skin irritation": "rash",
    
    # ==================== Breathing ====================
    "short of breath": "shortness of breath",
    "can't breathe": "shortness of breath",
    "breathlessness": "shortness of breath",
    "trouble breathing": "shortness of breath",
    "wheezing": "wheezing", # REFINED: 'wheezing' is a distinct and important symptom

    # ==================== Dizziness ====================
    "feel dizzy": "dizziness",
    "feeling dizzy": "dizziness",
    "spinning sensation": "vertigo", # REFINED: More specific term
    "lightheaded": "dizziness",
    "feel faint": "presyncope", # REFINED: More specific term
    
    # ==================== GI / Stomach ====================
    "stomach ache": "abdominal pain",
    "tummy pain": "abdominal pain",
    "belly pain": "abdominal pain",
    "stomach cramps": "abdominal cramps",
    "gut pain": "abdominal pain",
    "diarrhea": "diarrhea",
    "loose motion": "diarrhea",
    "constipated": "constipation",
    "bloated": "bloating",
    "gas": "bloating",
    "acid reflux": "heartburn",
    "indigestion": "dyspepsia", # REFINED: More specific term
    
    # ==================== Urinary ====================
    "frequent urination": "frequent urination",
    "urinating often": "frequent urination",
    "always thirsty": "excessive thirst",
    "very thirsty": "excessive thirst",
    "painful urination": "painful urination",
    "burning urination": "painful urination",
    "burning when peeing": "painful urination",
    "cloudy urine": "cloudy urine", # CHANGED: Mapped to symptom, not disease
    "getting up to pee at night": "nocturia",

    # ==================== Neurological ====================
    "numbness": "numbness", # REFINED: Kept simple term
    "tingling": "tingling",
    "pins and needles": "tingling",
    "shaky": "tremor",
    "trembling": "tremor",
    "muscle weakness": "weakness",
    "weak limbs": "weakness",

    # ==================== Psychological ====================
    "anxious": "anxiety",
    "nervous": "anxiety",
    "sad": "low mood",
    "disoriented": "confusion",
    "confused": "confusion",
    "trouble sleeping": "insomnia",

    # ==================== Musculoskeletal ====================
    "joint pain": "joint pain",
    "muscle pain": "muscle pain",
    "body ache": "muscle pain",
    "sore muscles": "muscle pain",
    "stiff joints": "joint stiffness",
    "pulled muscle": "muscle strain",
    "tendon pain": "tendon pain", # CHANGED: Mapped to symptom, not disease
    "heel pain": "heel pain",
    "lower back pain": "lower back pain"
}

modifiers = [
    "constant", "throbbing", "sharp", "mild", "severe", "intermittent",
    "on and off", "persistent", "sudden", "gradual", "spinning", "dull"
]

# -------------------- Symptom Extraction --------------------
from rapidfuzz import process, fuzz
def extract_symptoms(text: str):
    text_lower = text.lower()
    extracted = set()

    # 1. Check for synonyms (keys) and map to standard terms (values)
    for synonym_key, standard_value in synonym_map.items():
        # Use regex for whole word matching to avoid partial matches
        if re.search(rf'\b{re.escape(synonym_key)}\b', text_lower):
            extracted.add(standard_value)

    # 2. Check for the standard terms (values) themselves
    # Get a unique set of all standard terms from the map
    all_standard_terms = set(synonym_map.values())
    for term in all_standard_terms:
        if re.search(rf'\b{re.escape(term)}\b', text_lower):
            extracted.add(term)
    
    # 3. Add NER-based entities (optional but good for coverage)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DISEASE":
            # Normalize the NER entity if it's a known synonym
            ner_symptom = ent.text.lower()
            standard_term = synonym_map.get(ner_symptom, ner_symptom)
            extracted.add(standard_term)

    return list(extracted)



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
    """
    Extract condition names from response with better parsing
    """
    lines = response.strip().split("\n")
    conditions = []
    for line in lines:
        line = line.strip()
        # Try multiple patterns to extract condition names
        patterns = [
            r"\d\.\s*Condition Name:\s*(.+)",
            r"\d\.\s*(.+?)(?:\s*Reason:|$)",
            r"Condition Name:\s*(.+)",
            r"\d\.\s*(.+?)(?:\n|$)"
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                condition = match.group(1).strip().lower()
                # Clean up the condition name
                condition = re.sub(r'\s*reason:.*$', '', condition, flags=re.IGNORECASE)
                conditions.append(condition)
                break

        if len(conditions) >= 2:
            break

    # If we couldn't extract conditions, return original response
    if not conditions:
        return response.lower().strip()

    # Return formatted conditions
    return ", ".join(conditions[:2])
 

# --------------------Fallback  --------------------
def apply_fallback_diagnosis(symptoms, context=""):
    """
    Provide reasonable diagnoses when main system fails
    """
    # Common symptom-to-condition mappings
    fallback_mappings = {
        "fever": ["influenza", "viral infection"],
        "headache": ["migraine", "tension headache"],
        "chest pain": ["asthma", "heart condition"],
        "nausea": ["gastroenteritis", "food poisoning"],
        "joint pain": ["arthritis", "rheumatoid arthritis"],
        "fatigue": ["anemia", "hypothyroidism"],
        "shortness of breath": ["asthma", "heart failure"],
        "blurred vision": ["diabetes", "eye strain"],
        "dizziness": ["low blood pressure", "dehydration"],
        "frequent urination": ["diabetes", "urinary tract infection"],
        "rash": ["allergic reaction", "dermatitis"],
        "cough": ["bronchitis", "pneumonia"],
        "abdominal pain": ["gastritis", "irritable bowel syndrome"]
    }
    # Find matching conditions
    suggested_conditions = []
    for symptom in symptoms:
        if symptom in fallback_mappings:
            suggested_conditions.extend(fallback_mappings[symptom])
    # If no matches, provide general conditions
    if not suggested_conditions:
        suggested_conditions = ["viral infection", "stress-related symptoms"]
    # Take first two unique conditions
    unique_conditions = list(dict.fromkeys(suggested_conditions))[:2]
    # Ensure we have exactly 2 conditions
    if len(unique_conditions) < 2:
        unique_conditions.append("general medical condition")
    return f"1. Condition Name: {unique_conditions[0]}\nReason: Based on symptom pattern and clinical presentation.\n2. Condition Name: {unique_conditions[1]}\nReason: Alternative diagnosis considering patient symptoms."


# -------------------- Diagnosis Generator --------------------
def generate_diagnosis(symptoms, followup_answers, extra_input="", age=None, gender=None, country=None):
    # Step 1: Normalize and structure follow-up input
    if isinstance(followup_answers, dict):
        all_answers = []
        for answers in followup_answers.values():
            all_answers.extend(answers)
    else:
        all_answers = [followup_answers.strip()] if followup_answers else []
 
    # Step 2: Add extra user input if available
    if extra_input:
        all_answers.append(f"Additional Notes: {extra_input}")
 
    # Step 3: Include demographic information
    demographics = []
    if age:
        demographics.append(f"Age: {age}")
    if gender:
        demographics.append(f"Gender: {gender}")
    if country:
        demographics.append(f"Country: {country}")
    if demographics:
        all_answers.insert(0, ". ".join(demographics))
 
    # Step 4: Join everything into a single context string
    context = ". ".join(all_answers) if all_answers else "No additional context provided."
    symptom_str = ", ".join(symptoms) if symptoms else "Not specified"
 
    # Step 5: IMPROVED PROMPT - More directive and specific
    query = f"""
    You are an expert medical diagnostic assistant with access to comprehensive medical knowledge.
    PATIENT PRESENTATION:
    Primary Symptoms: {symptom_str}
    Additional Context: {context}
    TASK: Identify the TWO most likely medical conditions based on the symptoms provided.
    MANDATORY REQUIREMENTS:
    1. You MUST provide exactly 2 diagnoses - never say "I don't know"
    2. Choose from well-known medical conditions
    3. Use your medical knowledge even if symptoms don't perfectly match
    4. Provide reasonable medical hypotheses based on symptom patterns
    5. Consider common conditions first, then rare ones
    RESPONSE FORMAT (STRICT):
    1. Condition Name: [specific medical condition]
    Reason: [clinical reasoning based on symptoms and context]
    2. Condition Name: [different medical condition]
    Reason: [clinical reasoning based on symptoms and context]
    EXAMPLES OF GOOD RESPONSES:
    - "diabetes" not "metabolic disorder"
    - "heart failure" not "cardiac condition"
    - "migraine" not "headache disorder"
    Always provide your best medical assessment. If uncertain, provide the most probable conditions based on symptom presentation.
    """
 
    # Step 6: Get response from LLM with fallback
    try:
        result = rag_chain.invoke({"question": query})
        response = result["answer"]
        # If response contains "I don't know" or similar, apply fallback
        if any(phrase in response.lower() for phrase in ["i don't know", "cannot find", "cannot answer", "not enough information"]):
            response = apply_fallback_diagnosis(symptoms, context)
        return response.strip()
    except Exception as e:
        print(f"Error in diagnosis generation: {e}")
        return apply_fallback_diagnosis(symptoms, context)

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

    print(f"Extracted symptoms: {', '.join(symptoms)}")
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

