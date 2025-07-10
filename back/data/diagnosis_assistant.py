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
synonym_map = {
    # ==================== General ====================
    "tired": "fatigue",
    "exhausted": "fatigue",
    "burned out": "fatigue",
    "worn out": "fatigue",
    "lethargic": "fatigue",
    "groggy": "fatigue",
    "lack of energy": "fatigue",
    "feeling weak": "fatigue",
    "fatigued": "fatigue",
    
    # ==================== Vision ====================
    "blurry vision": "blurred vision",
    "can't see clearly": "blurred vision",
    "dim vision": "blurred vision",
    "spots in vision": "blurred vision",
    "seeing spots": "blurred vision",
    "floaters": "blurred vision",
    "flashes of light": "photopsia",
    "vision fades": "blurred vision",
    "vision problems": "blurred vision",
    "seeing double": "diplopia",
    "double vision": "diplopia",
    "crossed eyes": "strabismus",
    "eye misalignment": "strabismus",
    "sensitive to light": "photophobia",
    "light sensitivity": "photophobia",

    # ==================== Headache / Nausea ====================
    "head pain": "headache",
    "hurting head": "headache",
    "pounding head": "headache",
    "aching head": "headache",
    "migraine": "headache",
    "feel nauseous": "nausea",
    "queasy": "nausea",
    "sick to stomach": "nausea",
    "want to throw up": "nausea",
    "puke": "nausea",
    "vomit": "nausea",
    "throwing up": "nausea",
    "retching": "nausea",
    "green around the gills": "nausea",
    "turned stomach": "nausea",

    # ==================== Fever ====================
    "feverish": "fever",
    "burning up": "fever",
    "high temperature": "fever",
    "hot body": "fever",
    "hot flush": "fever",
    "temperature": "fever",
    "chills": "fever",

    # ==================== Chest ====================
    "chest tightness": "chest pain",
    "chest discomfort": "chest pain",
    "burning in chest": "chest pain",
    "tight chest": "chest pain",
    "pressure in chest": "chest pain",
    "pain in chest when breathing": "chest pain",
    "squeezing chest": "chest pain",
    "heart racing": "palpitations",
    "pounding heart": "palpitations",

    # ==================== Cold Symptoms ====================
    "runny nose": "rhinorrhea",
    "sneezing": "rhinorrhea",
    "sniffles": "rhinorrhea",
    "drippy nose": "rhinorrhea",
    "stuffy nose": "nasal congestion",
    "congested": "nasal congestion",
    "blocked nose": "nasal congestion",
    "sore throat": "throat pain",
    "scratchy throat": "throat pain",
    "hoarse voice": "hoarseness",
    "hoarseness": "hoarseness",
    "coughing": "cough",
    "cough with phlegm": "productive cough",
    "green mucus": "productive cough",
    "phlegm": "productive cough",
    "mucus": "productive cough",

    # ==================== Skin ====================
    "red spots": "rash",
    "itchy skin": "rash",
    "itchy spots": "rash",
    "hives": "rash",
    "skin bumps": "rash",
    "skin irritation": "rash",
    "redness on skin": "rash",
    "peeling skin": "rash",
    "dry skin": "rash",

    # ==================== Breathing ====================
    "short of breath": "shortness of breath",
    "can't breathe": "shortness of breath",
    "can't catch breath": "shortness of breath",
    "breathlessness": "shortness of breath",
    "wheezing": "shortness of breath",
    "trouble breathing": "shortness of breath",

    # ==================== Dizziness ====================
    "feel dizzy": "dizziness",
    "feeling dizzy": "dizziness",
    "spinning sensation": "dizziness",
    "lightheaded": "dizziness",
    "feel faint": "dizziness",
    "loss of balance": "dizziness",

    # ==================== GI / Stomach ====================
    "stomach ache": "abdominal pain",
    "tummy pain": "abdominal pain",
    "belly pain": "abdominal pain",
    "pain after eating": "abdominal pain",
    "diarrhea": "diarrhea",
    "loose motion": "diarrhea",
    "constipated": "constipation",
    "bloated": "bloating",
    "gas": "bloating",
    "acid reflux": "heartburn",
    "burning in stomach": "heartburn",
    "loss of appetite": "anorexia",
    "can’t eat": "anorexia",
    "skipped meals": "anorexia",

    # ==================== Urinary ====================
    "frequent urination": "polyuria",
    "urinating often": "polyuria",
    "excessive urination": "polyuria",
    "always thirsty": "polydipsia",
    "very thirsty": "polydipsia",
    "excessive thirst": "polydipsia",
    "painful urination": "dysuria",
    "burning urination": "dysuria",
    "burning when peeing": "dysuria",
    "cloudy urine": "urinary tract infection",
    "getting up to pee at night": "nocturia",

    # ==================== Neurological ====================
    "numbness": "paresthesia",
    "tingling": "paresthesia",
    "pins and needles": "paresthesia",
    "hand numbness": "paresthesia",
    "shaky": "tremors",
    "trembling": "tremors",
    "trembling hands": "tremors",
    "hand tremors": "tremors",
    "shaking hands": "tremors",
    "muscle weakness": "weakness",
    "feeling weak": "weakness",
    "weak limbs": "weakness",
    "unsteady": "balance issues",

    # ==================== Psychological ====================
    "anxious": "anxiety",
    "nervous": "anxiety",
    "panic attacks": "anxiety",
    "low mood": "depression",
    "sad": "depression",
    "disoriented": "confusion",
    "confused": "confusion",
    "mental fog": "confusion",
    "forgetfulness": "memory loss",
    "can't concentrate": "concentration difficulty",
    "sleep issues": "insomnia",
    "trouble sleeping": "insomnia",

    # ==================== Cardiovascular ====================
    "swollen feet": "edema",
    "ankle swelling": "edema",
    "leg swelling": "edema",
    "fluid retention": "edema",
    "pounding heart": "palpitations",
    "heart fluttering": "palpitations",

    # ==================== Musculoskeletal ====================
    "joint pain": "arthralgia",
    "knee pain": "joint pain",
    "shoulder pain": "joint pain",
    "muscle pain": "myalgia",
    "body ache": "myalgia",
    "sore muscles": "myalgia",
    "stiff joints": "joint stiffness",

    # ==================== Reproductive / Urinary ====================
    "irregular periods": "menstrual irregularity",
    "heavy periods": "menorrhagia",
    "painful periods": "dysmenorrhea",
    "vaginal discharge": "discharge",
    "burning while urinating": "dysuria",

    # Muscle Strain
    "pulled muscle": "muscle strain",
    "muscle tear": "muscle strain",
    "strained muscle": "muscle strain",
    "muscle injury": "muscle strain",
    "muscle soreness": "muscle strain",

    # Tendonitis
    "tendon pain": "tendonitis",
    "joint tendon pain": "tendonitis",
    "tendinitis": "tendonitis",  # spelling variant
    "tendon inflammation": "tendonitis",

    # Myositis
    "muscle inflammation": "myositis",
    "muscle tenderness": "myositis",
    "muscle fatigue": "myositis",
    "difficulty climbing stairs": "myositis",

    # Fibromyalgia
    "chronic muscle pain": "fibromyalgia",
    "widespread pain": "fibromyalgia",
    "muscle ache all over": "fibromyalgia",
    "fibro pain": "fibromyalgia",
    "tender points": "fibromyalgia",
    "body pain with fatigue": "fibromyalgia",

    # Rhabdomyolysis
    "dark urine after exercise": "rhabdomyolysis",
    "muscle breakdown": "rhabdomyolysis",
    "severe muscle pain": "rhabdomyolysis",
    "muscle swelling": "rhabdomyolysis",
    "rhabdo": "rhabdomyolysis",

    # Muscle Cramp
    "charley horse": "muscle cramp",
    "leg cramp": "muscle cramp",
    "sudden muscle pain": "muscle cramp",
    "tight muscle": "muscle cramp",
    "cramping": "muscle cramp",
    "muscle spasm": "muscle cramp",

    # Sinusitis
    "facial pain": "facial pain",
    "nasal congestion": "nasal congestion",
    "stuffed nose": "nasal congestion",
    "postnasal drip": "postnasal drip",

    # Conjunctivitis
    "red eyes": "red eyes",
    "eye redness": "red eyes",
    "eye discharge": "discharge",
    "watery eyes": "tearing",
    "itchy eyes": "itching",

    # Otitis Media
    "ear pain": "ear pain",
    "earache": "ear pain",
    "hearing loss": "hearing loss",
    "irritability": "irritability",

    # Anemia
    "pallor": "pallor",
    "dizziness": "dizziness",
    "lightheadedness": "dizziness",
    "tiredness": "fatigue",
    "shortness of breath": "shortness of breath",

    # Gallstones
    "upper abdominal pain": "upper abdominal pain",
    "gallbladder pain": "upper abdominal pain",

    # Bacterial Vaginosis
    "vaginal discharge": "vaginal discharge",
    "vaginal odor": "odor",
    "vaginal burning": "burning",

    # Tension Headache
    "dull headache": "dull head pain",
    "tight scalp": "scalp tightness",
    "neck stiffness": "neck stiffness",

    # Plantar Fasciitis
    "heel pain": "heel pain",
    "morning foot pain": "worse in morning",

    # Scabies
    "intense itching": "intense itching",
    "mite rash": "rash",
    "burrow marks": "burrow tracks",

    # Eczema
    "red patches": "red patches",
    "skin dryness": "dry skin",
    "cracked skin": "cracking",

     # Bronchitis
    "productive cough": "cough",
    "wheezing": "wheezing",
    "mucus": "mucus",
    "chest discomfort": "chest discomfort",

    # Influenza
    "muscle aches": "muscle aches",
    "body ache": "muscle aches",

    # Heat Stroke
    "high temperature": "high body temp",
    "dry skin": "dry skin",
    "rapid heartbeat": "rapid pulse",
    "heat exhaustion": "high body temp",

    # Food Poisoning
    "stomach cramps": "abdominal cramps",
    "loose motion": "diarrhea",

    # Lactose Intolerance
    "milk allergy": "lactose intolerance",
    "gas": "gas",
    "bloating": "bloating",

    # IBS
    "constipation": "constipation",
    "diarrhea": "diarrhea",
    "gut pain": "abdominal pain",

    # Seasonal Allergies
    "hay fever": "seasonal allergies",
    "runny nose": "runny nose",
    "nasal congestion": "congestion",

    # Depression
    "low mood": "low mood",
    "loss of interest": "low mood",
    "sadness": "low mood",
    "appetite loss": "appetite changes",

    # Anxiety
    "worry": "worry",
    "nervousness": "restlessness",
    "tight chest": "muscle tension",

    # Menstrual Cramps
    "period pain": "lower abdominal pain",
    "cramps": "lower abdominal pain",

    # Dyspepsia
    "indigestion": "upper abdominal discomfort",
    "burping": "burping",
    "early fullness": "early satiety",

    # Sciatica
    "leg pain": "leg tingling",
    "back pain": "lower back pain",
    "nerve pain": "leg tingling",

    # Constipation
    "hard stools": "hard stools",
    "difficulty pooping": "straining",

    # Tonsillitis
    "pain swallowing": "difficulty swallowing",
    "throat pain": "sore throat",
    "swollen tonsils": "swollen tonsils",

    # Ringworm
    "fungal rash": "itchy ring-shaped rash",
    "scaly rash": "scaling",
    "red ring": "redness",

    # ==================== Others ====================
    "passed out": "syncope",
    "fainting": "syncope",
    "night sweats": "sweating",
    "sweating a lot": "sweating",
    "sun exposure": "heat exhaustion",
    "heatstroke": "heat exhaustion",
    "overheated": "heat exhaustion",

}


modifiers = [
    "constant", "throbbing", "sharp", "mild", "severe", "intermittent",
    "on and off", "persistent", "sudden", "gradual", "spinning", "dull"
]

# -------------------- Symptom Extraction --------------------
from rapidfuzz import process, fuzz

def extract_symptoms(text: str, threshold: int = 92):
    text_lower = text.lower()
    doc = nlp(text)

    ner_extracted = [ent.text.lower() for ent in doc.ents if ent.label_ == "DISEASE"]

    synonyms_found = []
    for key in synonym_map:
        if key in text_lower:
            synonyms = synonym_map[key]
            if isinstance(synonyms, list):
                synonyms_found.extend(synonyms)
            else:
                synonyms_found.append(synonyms)

    keyword_matched = [sym for sym in symptom_vocab if re.search(rf'\b{re.escape(sym)}\b', text_lower)]


    # Flatten and deduplicate
    all_raw = ner_extracted + synonyms_found + keyword_matched
    flattened = [item for item in all_raw if isinstance(item, str)]
    combined_raw = list(set(flattened))

    return combined_raw


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

