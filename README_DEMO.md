# OSS Community Agent – Demo Script (Optional)

This demo script walks you through the key scenarios to showcase during a live demo.

1) Setup
- Ensure you have a Python 3.11+ environment
- Copy .env.example to .env and fill Reddit credentials (or set LLM_PROVIDER=none for offline demo)
- Install dependencies: pip install -r infra/requirements.txt

2) Launch the UI
- Windows: pwsh -ExecutionPolicy Bypass -File .\start.ps1 -UIOnly
- Cross-platform: python run_ui.py

3) Walkthrough
- Dashboard: Show Key Metrics, charts, and Recent Activity
- Settings: Walk viewers through API credentials and LLM provider selection
- RAG Configuration: Explain how docs in data/corpus are indexed; click Rebuild Index (if wired)
- Approval Queue: Show pending requests; open one and explain citations, moderation score, and safety
- Logs: Show filter/search capabilities and exports
- Monitor: Start a Manual Scan and observe the run status and results

4) Human-in-the-loop
- In Approval, edit a drafted reply and approve it (if DRY_RUN=False and credentials set, reply will be posted)

5) Closing
- Summarize safety (moderation + HITL), transparency (plan and logs), and productivity gains.

