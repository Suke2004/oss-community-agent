"""
rag_tool.py
Retrieval-Augmented Generation Tool for OSS Community Agent.

Features:
- Load project docs from data/corpus/
- Index docs in ChromaDB for vector search
- Fallback to keyword search if ChromaDB is unavailable
- Provide draft replies with inline citations

Dependencies:
chromadb>=0.4.0
(optional) openai for LLM & embeddings
"""

import os
import re
import uuid
from typing import List, Dict, Optional

# Optional: ChromaDB imports
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "corpus")
DEFAULT_COLLECTION = "oss_docs"


# ===========================
# DOC LOADING & PARSING
# ===========================

def load_docs() -> List[Dict]:
    """
    Load all markdown files and split into sections.
    Returns: List of {file, section, content}
    """
    docs = []
    for root, _, files in os.walk(CORPUS_DIR):
        for fname in files:
            if fname.endswith(".md"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                sections = split_into_sections(text)
                for sec in sections:
                    docs.append({
                        "file": fname,
                        "section": sec["heading"],
                        "content": sec["content"]
                    })
    return docs


def split_into_sections(text: str) -> List[Dict]:
    """
    Split markdown into sections by heading.
    """
    sections = []
    pattern = r"(#+ .+)"
    parts = re.split(pattern, text)
    current_heading = "Introduction"
    current_content = []

    for part in parts:
        if re.match(pattern, part):
            if current_content:
                sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})
                current_content = []
            current_heading = part.strip("# ").strip()
        else:
            current_content.append(part)

    if current_content:
        sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})

    return sections


# ===========================
# VECTOR STORE INITIALIZATION
# ===========================

def initialize_vector_store(persist_directory="./vector_store"):
    """
    Initialize ChromaDB client and return it.
    """
    if not chromadb:
        raise ImportError("ChromaDB is not installed. Run `pip install chromadb`.")
    
    client = chromadb.PersistentClient(path=persist_directory)
    return client


def refresh_docs(client, collection_name=DEFAULT_COLLECTION):
    """
    Re-index all docs into ChromaDB collection.
    Each section is stored as a separate document with metadata.
    """
    docs = load_docs()
    collection = client.get_or_create_collection(collection_name)
    
    # Clear old entries
    try:
        collection.delete(where={})
    except:
        pass

    ids, texts, metadatas = [], [], []
    for doc in docs:
        doc_id = str(uuid.uuid4())
        ids.append(doc_id)
        texts.append(doc["content"])
        metadatas.append({"file": doc["file"], "section": doc["section"]})

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Indexed {len(docs)} sections into ChromaDB.")


# ===========================
# SEARCH
# ===========================

def search_docs(query: str, client=None, use_vector=True, top_k=3) -> List[Dict]:
    """
    Search docs using ChromaDB (vector) if available, else fallback to keyword.
    Returns: List of {file, section, content, score}
    """
    if use_vector and client:
        try:
            collection = client.get_or_create_collection(DEFAULT_COLLECTION)
            results = collection.query(query_texts=[query], n_results=top_k)
            matches = []
            for i in range(len(results["documents"][0])):
                matches.append({
                    "file": results["metadatas"][0][i]["file"],
                    "section": results["metadatas"][0][i]["section"],
                    "content": results["documents"][0][i],
                    "score": results["distances"][0][i] if "distances" in results else 0
                })
            return matches
        except Exception as e:
            print("Vector search failed, falling back to keyword search:", e)

    # Fallback keyword search
    docs = load_docs()
    query_terms = query.lower().split()
    results = []

    for doc in docs:
        text = f"{doc['section']} {doc['content']}".lower()
        score = sum(text.count(term) for term in query_terms)
        if score > 0:
            results.append({**doc, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ===========================
# DRAFT REPLY
# ===========================

def draft_reply(query: str, client=None, use_llm=False) -> str:
    """
    Generate a concise reply for Reddit using relevant docs.
    """
    results = search_docs(query, client=client)
    if not results:
        return "I couldn't find relevant information in the documentation."

    reply_lines = ["Here’s what I found in the documentation:\n"]
    for res in results:
        snippet = res['content'][:300].replace("\n", " ") + ("..." if len(res['content']) > 300 else "")
        citation = f"[from {res['file']}:{res['section']}]"
        reply_lines.append(f"- {snippet} {citation}")
    return "\n".join(reply_lines)


# ===========================
# TEST
# ===========================
if __name__ == "__main__":
    if chromadb:
        client = initialize_vector_store()
        refresh_docs(client)
    else:
        client = None

    q = "How do I install the library?"
    print(draft_reply(q, client=client))
