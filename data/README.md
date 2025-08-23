# The Agent's Knowledge Base

This `corpus` directory serves as the knowledge base for our AI agent's Retrieval-Augmented Generation (RAG) tool. The agent reads and indexes the files in this directory to answer user questions on platforms like Reddit.

## How to Add New Data
To add new information to the agent's knowledge base, simply place a new markdown (`.md`) file inside this directory. Each file should contain well-structured text, such as documentation, FAQs, or troubleshooting guides. The RAG tool will automatically discover and index these new files on startup.

## TODO:
- [ ] **Data Versioning:** Implement a system to version the knowledge base. This could involve using Git tags or a simple version file.
- [ ] **Automated Ingestion:** Build a script that can pull new documentation directly from a wiki or website and automatically convert it to markdown.
- [ ] **Support Multiple Formats:** Extend the RAG tool to handle other file types like `.rst`, `.html`, or even `.pdf` for more comprehensive knowledge.