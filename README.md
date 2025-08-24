# OSS Community Auto-Responder 🤖

### An AI agent to help open-source maintainers manage community support on Reddit, grounded in project documentation.


## 💡 The Problem

Open-source project maintainers spend countless hours answering repetitive questions across forums like Reddit, Quora, and Discord. This not only consumes valuable time that could be spent on development but also leads to burnout and delayed responses for community members.

## ✨ Our Solution: Human-in-the-Loop Auto-Responder

The OSS Community Auto-Responder is a safe, controllable AI agent designed to alleviate this burden. Using the **Portia AI** framework, it autonomously:
1.  **Watches** for new questions about a project on Reddit.
2.  **Drafts** a high-quality, doc-grounded answer.
3.  **Pauses** for human approval.
4.  **Posts** the reply only after the maintainer gives the final okay.

This approach ensures that maintainers retain complete control over all public-facing communication while saving significant time. The entire process is auditable and transparent, from the agent's explicit **plan** to the final, human-approved post.

## 🚀 Key Features

* **Portia-Powered Agentic Workflow:** Our agent uses Portia's core features to orchestrate complex tasks, including `Plan` creation, stateful execution, and `Clarification` for human-in-the-loop (HITL) control. This is the **central, mandatory component** of our submission.
* **Documentation-Grounded Replies (RAG):** The agent indexes a project's documentation, wiki, and FAQs to generate accurate and trustworthy responses with clear citations.
* **Multi-Tool Integration:** The agent leverages a custom **Reddit Tool** (using PRAW) and a local **RAG Tool** to perform its tasks.
* **Simple, Transparent UX:** A single-screen Streamlit UI makes the agent's plan, proposed actions, and approval workflow obvious in seconds, demonstrating a clear and safe process.

***

## 💻 Tech Stack

* **Agent Framework:** Portia AI SDK
* **Frontend:** Streamlit
* **Backend:** Python 3.11+
* **Tools:**
    * **Reddit Tool:** PRAW
    * **RAG Tool:** Custom implementation
    * **Moderation Tool:** Custom lightweight filters
    * **Scraping:** (Optional) ScrapeGraphAI

***

## 📁 Project Structure
```py
oss-community-agent/
├── apps/
│   ├── agent/
│   │   └── main.py                     # Main agent orchestration logic (Portia)
│   └── ui/
│       └── streamlit_app.py            # Streamlit UI for the demo
├── data/
│   └── corpus/                         # Place for project documentation, wiki, etc.
│       └── example_doc.md
├── infra/
│   ├── .env.example                    # Template for environment variables
│   └── requirements.txt                # All Python dependencies
├── tools/
│   ├── moderation_tool.py              # Safety and guardrails
│   ├── rag_tool.py                     # Retrieval-Augmented Generation logic
│   ├── reddit_tool.py                  # PRAW wrapper for Reddit API
│   └── scrape_tool.py                  # (Optional) ScrapeGraphAI web scraper
├── .gitignore                          # Git ignore file
├── README.md                           # This file
└── README_DEMO.md                      # Step-by-step demo script (optional, see README_DEMO.md if present)
```

***

## ⚙️ Getting Started

### Prerequisites

* Python 3.11 or newer (required by `portia-sdk-python`).
* A Reddit API account with a registered script app.
* A virtual environment manager (`uv` is recommended).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/BennyPerumalla/oss-community-agent.git](https://github.com/BennyPerumalla/oss-community-agent.git)
    cd oss-community-agent
    ```
2.  **Create and activate a virtual environment with a compatible Python version:**
    ```bash
    uv venv
    uv pip install -r infra/requirements.txt
    ```
    * On Windows, activate with: `.venv\Scripts\activate`

3.  **Configure environment variables:**
    * Copy the example file: `cp infra/.env.example infra/.env`
    * Open `infra/.env` and fill in your Reddit API credentials and set `DRY_RUN=True` for initial testing.

### Running the Demo

1.  Windows (PowerShell):
    - UI only: `pwsh -ExecutionPolicy Bypass -File .\start.ps1 -UIOnly`
    - Full system (UI + backend): `pwsh -ExecutionPolicy Bypass -File .\start.ps1`

2.  Cross-platform via Python launchers:
    - UI only: `python run_ui.py`
    - Full system: `python run_full_system.py`

3.  Direct Streamlit (advanced):
    ```bash
    python -m streamlit run apps/ui/streamlit_app.py
    ```
4.  A web browser will open, and you'll see the agent's UI. This interface is the core of your demo.

***

## 🗺️ Roadmap & Future Improvements

* Integrate a vector database (e.g., ChromaDB, Milvus) for more advanced and efficient RAG.
* Add support for other platforms like Discord or Slack for approval notifications.
* Implement metrics and dashboards to show time saved and maintainer engagement over time.

***

## 🏆 AgentHack 2025 Submission Checklist

* ✅ **Portia AI:** The project is built on the Portia framework, leveraging its core `Plan` and `Clarification` features.
* ✅ **Implementation Quality:** The project includes multiple tools and a clear, functional architecture.
* ✅ **Creativity & Originality:** The human-in-the-loop, doc-grounded, cross-forum approach is a unique solution to a common OSS problem.
* ✅ **Potential Impact:** The project addresses a clear pain point for maintainers, with metrics to demonstrate time savings.
* ✅ **Aesthetics & UX:** The Streamlit UI provides a clean, auditable view of the agent's workflow.

***

## 📧 Contact

For questions or support, please open a GitHub issue or contact us directly.

- Benny Perumalla <benny01r@gmail.com>
- Md. Irshad Siddi <mohammadirshadsiddi@gmail.com>
- Sukesh Reddy <lyricsofsongs96@gmail.com>
- Hareeswar Reddy <ahreddy05@gmail.com>