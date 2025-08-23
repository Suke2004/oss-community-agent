# tools/moderation_tool.py

import re
from typing import Dict, Any, List

# A simple list of keywords to flag. This is a basic implementation.
# TODO: Augment with a more comprehensive, community-sourced list or an external API.
#       Consider using a library like 'profanity-check' or a service like OpenAI's Moderation API.
FLAGGED_KEYWORDS = [
    "personal information",
    "private details",
    "phone number",
    "email address",
    "password",
    "ssn",
    "social security number",
    "credit card",
    "unsafe command",
]

# Regular expressions for common PII patterns.
# This provides a basic level of PII detection without external dependencies.
PII_PATTERNS = {
    "phone_number": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "email_address": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
}

def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyzes the given text for potential moderation issues.

    This function performs a series of checks and returns a structured
    report. The checks include profanity, personally identifiable information (PII),
    and a list of flagged keywords.

    Args:
        text (str): The text to be analyzed.

    Returns:
        Dict[str, Any]: A dictionary containing a summary of the moderation results.
    """
    report = {
        "is_flagged": False,
        "flags": []
    }

    # TODO: Implement a more robust profanity filter.
    #       A simple list can be easily bypassed. A better solution would use
    #       a machine learning model or a specialized library like `better-profanity`.
    check_profanity(text, report)

    check_pii(text, report)
    
    check_keywords(text, report)

    return report

def check_profanity(text: str, report: Dict[str, Any]):
    """
    Performs a basic check for profane language.

    TODO:
    - [ ] Replace this with a robust library (e.g., `better-profanity`, `profanity-check`).
    - [ ] The current list is just a placeholder and can be easily bypassed.
    """
    profane_words = ["badword1", "badword2", "inappropriate_term"]
    if any(word in text.lower() for word in profane_words):
        report["is_flagged"] = True
        report["flags"].append({"type": "profanity", "message": "Contains offensive language."})

def check_pii(text: str, report: Dict[str, Any]):
    """
    Checks for common PII patterns using regular expressions.

    TODO:
    - [ ] Enhance PII detection using a dedicated library (e.g., Microsoft's `Presidio`).
    - [ ] The regex patterns can produce false positives. Add context-aware validation.
    """
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            report["is_flagged"] = True
            report["flags"].append({"type": "pii", "message": f"Contains potential {pii_type}."})
            
def check_keywords(text: str, report: Dict[str, Any]):
    """
    Checks for a list of predefined flagged keywords.
    """
    for keyword in FLAGGED_KEYWORDS:
        if keyword.lower() in text.lower():
            report["is_flagged"] = True
            report["flags"].append({"type": "keyword", "message": f"Contains flagged keyword: '{keyword}'."})

# --- Main function for local testing ---
if __name__ == "__main__":
    test_cases: List[str] = [
        "This is a great library, you guys are awesome!",
        "I need help with a stupid issue, this is so frustrating.",
        "My phone number is 123-456-7890. Please call me.",
        "Contact me at my_email@example.com for more details.",
        "I found a bug. This is an unsafe command and could break things.",
        "Just some normal text with no issues."
    ]

    for i, test_text in enumerate(test_cases):
        print(f"--- Test Case {i+1} ---")
        print(f"Input: '{test_text}'")
        result = analyze_text(test_text)
        print(f"Result: {json.dumps(result, indent=2)}")
        print("-" * 20)