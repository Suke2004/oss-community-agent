from pathlib import Path
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%asctime]: %(message)s')

list_of_files = [
    "src/__init__.py",
    "apps/agent/main.py",
    "app/ui/streamlit_app.py",
    "data/corpus/example_doc.md",
    "infra/.env.example",
    "infra/requirements.txt",
    "tools/moderation_tools.py",
    "tools/main.cpp",
    "tools/rag_tool.py",
    "tools/reddit_tool.py",
    "tools/scrape_tool.py",
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir !="":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    if(not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating file: {filepath}")
    else:
        logging.info(f"{filename} is already exists and not empty.")

        