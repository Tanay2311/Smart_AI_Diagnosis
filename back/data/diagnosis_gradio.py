required_modules = [
    "os",
    "re",
    "time",
    "warnings",
    "pandas",
    "spacy",
    "langchain.memory",
    "langchain.chains",
    "langchain_community.embeddings",  # alternative to langchain_huggingface
    "langchain_chroma",
    "langchain_community.document_loaders",
    "langchain_google_genai",
    "dotenv",
]

for module in required_modules:
    try:
        __import__(module)
        print(f"✅ {module} is installed.")
    except ImportError as e:
        print(f"❌ {module} is NOT installed. ({e.__class__.__name__})")
