import shutil
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PERSIST_DIR = os.path.join(BASE_DIR, "rag_index")

shutil.rmtree(PERSIST_DIR) 
