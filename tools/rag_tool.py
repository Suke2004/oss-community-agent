# tools/rag_tool.py

import os
from typing import Dict, List, Tuple
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.embeddings import OllamaEmbeddings # A great open-source embedding model
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# TODO: Replace with your actual preferred LLM. For an open-source approach,
#       consider using a local model with Ollama, or a service like Groq.
#       from langchain_groq import ChatGroq
#       from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Hardcoded for a simple, fast demo
KNOWLEDGE_BASE_PATH = "data/corpus/"
VECTOR_DB_PATH = "rag_db"

class RAGTool:
    """
    A tool for Retrieval-Augmented Generation (RAG) over a local document corpus.

    This tool handles data ingestion, document indexing, retrieval, and
    answer generation. It is designed to be modular for future enhancements.
    """

    def __init__(self):
        """Initializes the RAG tool by setting up the document retriever."""
        self.vectorstore = None
        self.llm = self._init_llm()
        self.retriever = None

        # TODO: Implement a system to check for corpus updates and re-index.
        #       This could involve checking file timestamps or using a checksum.
        self._load_or_create_vectorstore()

    def _init_llm(self):
        """Initializes the Large Language Model."""
        # This is a placeholder for your LLM of choice.
        # It reads from the environment variable 'OPENAI_API_KEY'.
        # TODO: Add logic to choose between different LLMs based on configuration
        #       (e.g., local Ollama, Groq, etc.)
        return ChatOpenAI(temperature=0.2)

    def _load_or_create_vectorstore(self):
        """
        Loads an existing vector store or creates a new one from the corpus.
        
        This method ensures that the tool is ready for queries without
        re-indexing the entire corpus every time.
        """
        if os.path.exists(VECTOR_DB_PATH):
            print("Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=VECTOR_DB_PATH,
                embedding_function=OllamaEmbeddings(model="nomic-embed-text")
            )
        else:
            print("No vector store found. Creating and indexing corpus...")
            docs = self._load_documents()
            chunked_docs = self._chunk_documents(docs)
            self._create_vectorstore(chunked_docs)
            print("Indexing complete.")

    def _load_documents(self) -> List[Document]:
        """
        Loads markdown documents from the knowledge base directory.
        
        TODO:
        - [ ] Add support for multiple document types (e.g., .txt, .pdf, .html).
        - [ ] Handle potential errors during file reading.
        """
        all_docs = []
        for filename in os.listdir(KNOWLEDGE_BASE_PATH):
            if filename.endswith(".md"):
                filepath = os.path.join(KNOWLEDGE_BASE_PATH, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    all_docs.append(Document(page_content=content, metadata={"source": filename}))
        return all_docs

    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits documents into smaller, semantically meaningful chunks.

        This is crucial for ensuring that the retrieved context fits within
        the LLM's token limit.
        """
        text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunked_docs = text_splitter.split_documents(documents)
        return chunked_docs

    def _create_vectorstore(self, chunked_docs: List[Document]):
        """Creates a new vector store from a list of documents."""
        # Using a simple in-memory vector store for the demo.
        # TODO: For production, use a more persistent and scalable solution
        #       like a self-hosted ChromaDB server or a cloud-based service.
        self.vectorstore = Chroma.from_documents(
            documents=chunked_docs,
            embedding=OllamaEmbeddings(model="nomic-embed-text"),
            persist_directory=VECTOR_DB_PATH
        )
        self.vectorstore.persist()
        self.retriever = self.vectorstore.as_retriever()
        
    def retrieve_and_generate(self, query: str) -> Tuple[str, List[Dict]]:
        """
        Retrieves relevant documents and generates a final answer.

        This is the core RAG method exposed to the agent.
        
        Args:
            query (str): The user's question or topic.

        Returns:
            Tuple[str, List[Dict]]: A tuple containing the drafted reply and a list of sources.
        """
        if not self.retriever:
            return "Error: RAG tool not properly initialized.", []

        # 1. Retrieval
        retrieved_docs = self.retriever.invoke(query)
        
        # 2. Generation Prompt
        template = """
        You are an expert open-source assistant. Your task is to provide a concise and helpful answer to a user's question based ONLY on the provided context.

        Instructions:
        - The answer must be based strictly on the context. Do not use any external knowledge.
        - If the context does not contain enough information, state that clearly and politely.
        - Include a citation for each piece of information, formatted as `[from <source_filename>]`.
        - Keep the answer brief and to the point.
        
        Context:
        {context}

        Question:
        {query}

        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        # 3. Augmentation and Generation
        context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Pass the context and query to the LLM
        final_prompt = prompt.format(context=context_text, query=query)
        response = self.llm.invoke(final_prompt)
        
        # 4. Citation and return
        # Here we map the retrieved documents to a more human-friendly format
        sources = [{"source": doc.metadata.get("source"), "content": doc.page_content} for doc in retrieved_docs]
        
        return response.content, sources

# --- Main function for local testing ---
if __name__ == "__main__":
    # This block allows you to test the RAG tool in isolation
    rag_tool = RAGTool()
    
    test_queries = [
        "What are the main requirements for installation?",
        "Where can I find the API key for Reddit?",
        "How do I use the human-in-the-loop approval?",
        "What are the planets in our solar system?" # A query not in the corpus
    ]

    for query in test_queries:
        print(f"\n--- Testing Query: '{query}' ---")
        answer, sources = rag_tool.retrieve_and_generate(query)
        print("Generated Answer:")
        print(answer)
        print("\nSources Used:")
        for source in sources:
            print(f"- {source['source']}")
        print("-" * 50)