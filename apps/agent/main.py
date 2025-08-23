# Inside your Portia plan in main.py
# ... after the RAG tool has drafted the reply

moderation_result = ModerationTool.analyze_text(drafted_reply)

if moderation_result["is_flagged"]:
    # The agent can then include this result in the clarification request.
    # This makes the "why" of the human-in-the-loop step explicit.
    clarification_request_prompt = (
        f"The drafted reply contains flagged content. Please review and approve.\n\n"
        f"**Flags:** {moderation_result['flags']}\n\n"
        f"Proposed Reply:\n{drafted_reply}"
    )
    # Portia.clarify(message=clarification_request_prompt)
else:
    # Proceed with a standard clarification request
    pass