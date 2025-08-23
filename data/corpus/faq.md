# Frequently Asked Questions

## How do I set up the environment?
Make sure you have Python 3.11+ installed. We recommend using `uv` and a virtual environment. You can set it up with `uv venv` and then install dependencies using `uv pip install -r infra/requirements.txt`.

## What are the Reddit API rate limits?
The Reddit API limits script apps to 60 requests per minute. You should implement exponential backoff and obey this limit to avoid getting banned.

## How does the human-in-the-loop approval work?
Our agent pauses its execution using Portia's `Clarification` feature. The drafted reply is sent to a Streamlit UI for your review. The agent will only proceed with a `post_reply` after you click 'Approve'.

## Why are my Reddit posts not showing up?
Please ensure your script's User-Agent is unique and descriptive, as required by Reddit's API. Also, check that you are posting in a public subreddit and not one that disallows bot submissions.