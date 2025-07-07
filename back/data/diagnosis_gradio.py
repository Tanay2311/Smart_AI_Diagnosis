import pandas as pd
import spacy
from fuzzywuzzy import process
import re
import gradio as gr
import warnings
import os
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

warnings.filterwarnings("ignore", category=FutureWarning)

# -------------------- Config --------------------
DATA_PATH = "medical_knowledge_clean.csv"
PERSIST_DIR = "./rag_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# -------------------- Load NLP --------------------
print("Loading spaCy model...")
nlp = spacy.load("en_ner_bc5cdr_md")

# -------------------- Load Dataset --------------------
print("Reading medical dataset...")
df = pd.read_csv(DATA_PATH)

def build_symptom_vocab(df):
    symptoms = set()
    for s in df["Symptoms"].dropna():
        symptoms.update([sym.strip().lower() for sym in s.split(",")])
    return sorted(symptoms)

symptom_vocab = build_symptom_vocab(df)

synonym_map = {
    "tired": "fatigue",
    "light sensitivity": "photophobia",
    "blurry vision": "blurred vision",
    "feeling nauseous": "nausea",
    "sweats": "sweating",
    "runny nose": "rhinorrhea"
}

def extract_symptoms(text):
    text_lower = text.lower()
    doc = nlp(text)
    ner_extracted = [ent.text.lower() for ent in doc.ents if ent.label_ == "DISEASE"]
    synonyms_found = [synonym_map[key] for key in synonym_map if key in text_lower]
    keyword_matched = [sym for sym in symptom_vocab if re.search(rf'\b{re.escape(sym)}\b', text_lower)]
    combined = list(set(ner_extracted + synonyms_found + keyword_matched))
    final_matches = set()
    for s in combined:
        match = process.extractOne(s, symptom_vocab)
        if match and match[1] > 85:
            final_matches.add(match[0])
    return sorted(final_matches)

# -------------------- Vector Store --------------------
print("Setting up vector index...")
if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
    print("Index not found. Creating new index...")
    loader = CSVLoader(file_path=DATA_PATH)
    docs = loader.load()
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectordb = Chroma.from_documents(docs, embedding=embedding, persist_directory=PERSIST_DIR)
    vectordb.persist()
else:
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding)

retriever = vectordb.as_retriever()

# -------------------- RAG Chain --------------------
llm = Ollama(model="llama3")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
rag_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    verbose=False
)

# -------------------- Chat Function --------------------
def chat_with_bot(user_input, history):
    if not user_input.strip():
        return history + [["You", "Please enter some symptoms."]], history

    symptoms = extract_symptoms(user_input)

    if symptoms:
        symptom_str = ", ".join(symptoms)
        system_query = f"The user is experiencing: {symptom_str}. What possible diagnoses could this indicate? Ask clarifying questions."
        intro = f"I've noted the following symptoms: **{symptom_str}**."
    else:
        system_query = user_input
        intro = "I couldn't extract any specific symptoms, but I’ll try to help."

    result = rag_chain.invoke({"question": system_query})
    raw_response = result["answer"].strip()
    parts = [intro] + re.split(r"\n\s*\n", raw_response)
    final_response = "\n\n".join(parts)
    history.append([user_input, final_response])
    return history, history

# -------------------- Gradio UI --------------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🩺 Smart AI Medical Assistant")
    chatbot = gr.Chatbot(show_label=False, height=500)
    msg = gr.Textbox(placeholder="Describe your symptoms here...", label="Your message")
    state = gr.State([])

    def respond(message, chat_history):
        return chat_with_bot(message, chat_history)

    msg.submit(respond, [msg, state], [chatbot, state])
    msg.submit(lambda: "", None, msg)

demo.launch(share=True)
